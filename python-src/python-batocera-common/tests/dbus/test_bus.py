from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import pytest
from dbus_fast import BusType, NameFlag, RequestNameReply
from dbus_fast.aio import MessageBus

from batocera_common.dbus.bus import Bus

if TYPE_CHECKING:
    from unittest.mock import MagicMock, NonCallableMock

    from _pytest.fixtures import SubRequest
    from pytest_mock import MockerFixture


type _EventsFixture = tuple[asyncio.Event | None, asyncio.Event | None]


@pytest.fixture
def mock_message_bus_connected(request: SubRequest) -> bool:
    return getattr(request, 'param', False)


def _create_method_events(request: SubRequest) -> _EventsFixture:
    if getattr(request, 'param', False):
        return asyncio.Event(), asyncio.Event()

    return None, None


@pytest.fixture
async def mock_message_bus_connect_events(request: SubRequest) -> _EventsFixture:
    return _create_method_events(request)


@pytest.fixture
async def mock_message_bus_wait_for_disconnect_events(request: SubRequest) -> _EventsFixture:
    return _create_method_events(request)


@pytest.fixture
def mock_message_bus_request_name_reply(request: SubRequest) -> RequestNameReply:
    return getattr(request, 'param', RequestNameReply.PRIMARY_OWNER)


@pytest.fixture
def mock_message_bus(
    mocker: MockerFixture,
    mock_message_bus_connected: bool,
    mock_message_bus_connect_events: _EventsFixture,
    mock_message_bus_request_name_reply: RequestNameReply,
    mock_message_bus_wait_for_disconnect_events: _EventsFixture,
) -> NonCallableMock:
    connect_begin_event, connect_finish_event = mock_message_bus_connect_events
    wait_for_disconnect_begin_event, wait_for_disconnect_finish_event = mock_message_bus_wait_for_disconnect_events

    async def connect_side_effect() -> NonCallableMock:
        if connect_begin_event is not None and connect_finish_event is not None:
            connect_begin_event.set()
            await connect_finish_event.wait()

        mock.connected = True
        return mock

    async def wait_for_disconnect_side_effect() -> None:
        if wait_for_disconnect_begin_event is not None and wait_for_disconnect_finish_event is not None:
            wait_for_disconnect_begin_event.set()
            await wait_for_disconnect_finish_event.wait()

        mock.connected = False

    mock = mocker.NonCallableMock(spec_set=MessageBus)
    mock.connected = mock_message_bus_connected
    mock.request_name.return_value = mock_message_bus_request_name_reply
    mock.connect.side_effect = connect_side_effect
    mock.wait_for_disconnect.side_effect = wait_for_disconnect_side_effect

    return mock


@pytest.fixture(autouse=True)
def mock_message_bus_cls(mocker: MockerFixture, mock_message_bus: NonCallableMock) -> MagicMock:
    return mocker.patch('batocera_common.dbus.bus.MessageBus', return_value=mock_message_bus)


class TestBus:
    def test_init(self, mock_message_bus_cls: MagicMock, mock_message_bus: NonCallableMock) -> None:
        bus = Bus()

        assert bus.bus_type == BusType.SYSTEM
        mock_message_bus_cls.assert_called_once_with(bus_type=BusType.SYSTEM)
        assert bus.connected is False
        assert bus.connecting is False
        assert bus.disconnecting is False

    def test_init_session(self, mock_message_bus_cls: MagicMock, mock_message_bus: NonCallableMock) -> None:
        bus = Bus(bus_type=BusType.SESSION)

        assert bus.bus_type == BusType.SESSION
        mock_message_bus_cls.assert_called_once_with(bus_type=BusType.SESSION)

    @pytest.mark.parametrize('mock_message_bus_connect_events', [True], indirect=True)
    async def test_connect(
        self,
        mock_message_bus: NonCallableMock,
        mock_message_bus_connect_events: tuple[asyncio.Event, asyncio.Event],
    ) -> None:
        begin_event, finish_event = mock_message_bus_connect_events
        bus = Bus()

        async with asyncio.timeout(1):
            task = asyncio.create_task(bus.connect())

            try:
                await begin_event.wait()

                assert bus.connected is False
                assert bus.connecting is True
                assert bus.disconnecting is False

                finish_event.set()
                await task

                assert bus.connected is True
                assert bus.connecting is False
                assert bus.disconnecting is False

            finally:
                task.cancel()
                await asyncio.gather(task, return_exceptions=True)

            mock_message_bus.connect.assert_awaited_once_with()

    async def test_connect_already_connected(self, mock_message_bus: NonCallableMock) -> None:
        bus = Bus()

        await bus.connect()

        mock_message_bus.connect.assert_awaited_once_with()

        assert bus.connected is True
        assert bus.connecting is False
        assert bus.disconnecting is False

        await bus.connect()

        mock_message_bus.connect.assert_awaited_once_with()

    @pytest.mark.parametrize('mock_message_bus_connect_events', [True], indirect=True)
    async def test_connect_while_connecting(
        self,
        mock_message_bus: NonCallableMock,
        mock_message_bus_connect_events: tuple[asyncio.Event, asyncio.Event],
    ) -> None:
        begin_event, finish_event = mock_message_bus_connect_events
        bus = Bus()

        async with asyncio.timeout(1):
            task = asyncio.create_task(bus.connect())

            try:
                await begin_event.wait()

                assert bus.connected is False
                assert bus.connecting is True
                assert bus.disconnecting is False

                with pytest.raises(RuntimeError, match='Cannot connect while a Bus lifecycle operation is in progress'):
                    await bus.connect()

                finish_event.set()
                await task

                assert bus.connected is True
                assert bus.connecting is False
                assert bus.disconnecting is False

            finally:
                task.cancel()
                await asyncio.gather(task, return_exceptions=True)

            mock_message_bus.connect.assert_awaited_once_with()

    @pytest.mark.parametrize('error', [RuntimeError('boom'), KeyboardInterrupt('boom')])
    async def test_connect_exception(self, mock_message_bus: NonCallableMock, error: BaseException) -> None:
        bus = Bus()
        mock_message_bus.connect.side_effect = error

        with pytest.raises(
            (
                RuntimeError,
                KeyboardInterrupt,
            ),
            match='boom',
            check=lambda e: e is error,
        ):
            await bus.connect()

        assert bus.connected is False
        assert bus.connecting is False
        assert bus.disconnecting is False

        with pytest.raises(RuntimeError, match='Bus is closed; create a new Bus'):
            await bus.connect()

        mock_message_bus.disconnect.assert_called_once_with()
        mock_message_bus.wait_for_disconnect.assert_not_awaited()

    async def test_connect_connection_lost(self, mock_message_bus: NonCallableMock) -> None:
        bus = Bus()

        await bus.connect()

        mock_message_bus.connect.assert_awaited_once_with()
        mock_message_bus.connect.reset_mock()

        assert bus.connected is True
        assert bus.connecting is False
        assert bus.disconnecting is False

        mock_message_bus.connected = False

        assert bus.connected is False

        with pytest.raises(RuntimeError, match='Bus connection was lost; create a new Bus'):
            await bus.connect()

        mock_message_bus.connect.assert_not_awaited()

    @pytest.mark.parametrize('mock_message_bus_wait_for_disconnect_events', [True], indirect=True)
    async def test_connect_while_disconnecting(
        self,
        mock_message_bus: NonCallableMock,
        mock_message_bus_wait_for_disconnect_events: tuple[asyncio.Event, asyncio.Event],
    ) -> None:
        begin_event, finish_event = mock_message_bus_wait_for_disconnect_events

        bus = Bus()
        await bus.connect()

        async with asyncio.timeout(1):
            task = asyncio.create_task(bus.disconnect())

            try:
                await begin_event.wait()

                assert bus.connected is False
                assert bus.connecting is False
                assert bus.disconnecting is True

                with pytest.raises(RuntimeError, match='Cannot connect while a Bus lifecycle operation is in progress'):
                    await bus.connect()

                finish_event.set()
                await task

                assert bus.connected is False
                assert bus.connecting is False
                assert bus.disconnecting is False

            finally:
                finish_event.set()
                task.cancel()
                await asyncio.gather(task, return_exceptions=True)

        mock_message_bus.connect.assert_awaited_once_with()

    async def test_connect_after_disconnect(self, mock_message_bus: NonCallableMock) -> None:
        bus = Bus()

        await bus.connect()
        await bus.disconnect()

        with pytest.raises(RuntimeError, match='Bus is closed; create a new Bus'):
            await bus.connect()

        mock_message_bus.connect.assert_awaited_once_with()

    @pytest.mark.parametrize('mock_message_bus_wait_for_disconnect_events', [True], indirect=True)
    async def test_disconnect(
        self,
        mock_message_bus: NonCallableMock,
        mock_message_bus_wait_for_disconnect_events: tuple[asyncio.Event, asyncio.Event],
    ) -> None:
        begin_event, finish_event = mock_message_bus_wait_for_disconnect_events

        bus = Bus()
        await bus.connect()

        async with asyncio.timeout(1):
            task = asyncio.create_task(bus.disconnect())

            try:
                await begin_event.wait()

                mock_message_bus.disconnect.assert_called_once_with()

                assert bus.connected is False
                assert bus.connecting is False
                assert bus.disconnecting is True

                finish_event.set()
                await task

                assert bus.connected is False
                assert bus.connecting is False
                assert bus.disconnecting is False

            finally:
                finish_event.set()
                task.cancel()
                await asyncio.gather(task, return_exceptions=True)

            mock_message_bus.disconnect.assert_called_once_with()
            mock_message_bus.wait_for_disconnect.assert_awaited_once_with()

    async def test_disconnect_already_disconnected(self, mock_message_bus: NonCallableMock) -> None:
        bus = Bus()
        await bus.connect()

        await bus.disconnect()

        assert bus.connected is False
        assert bus.connecting is False
        assert bus.disconnecting is False

        await bus.disconnect()

        mock_message_bus.disconnect.assert_called_once_with()
        mock_message_bus.wait_for_disconnect.assert_awaited_once_with()

    async def test_disconnect_never_connected(self, mock_message_bus: NonCallableMock) -> None:
        bus = Bus()

        await bus.disconnect()

        assert bus.connected is False
        assert bus.connecting is False
        assert bus.disconnecting is False

        mock_message_bus.disconnect.assert_called_once_with()
        mock_message_bus.wait_for_disconnect.assert_not_awaited()

    async def test_disconnect_failure(self, mock_message_bus: NonCallableMock) -> None:
        mock_message_bus.wait_for_disconnect.side_effect = RuntimeError('boom')
        bus = Bus()
        await bus.connect()

        with pytest.raises(RuntimeError, match='boom'):
            await bus.disconnect()

        assert bus.connected is False
        assert bus.connecting is False
        assert bus.disconnecting is False

        mock_message_bus.disconnect.assert_called_once_with()
        mock_message_bus.wait_for_disconnect.assert_awaited_once_with()

    @pytest.mark.parametrize('mock_message_bus_connect_events', [True], indirect=True)
    async def test_disconnect_while_connecting(
        self,
        mock_message_bus: NonCallableMock,
        mock_message_bus_connect_events: tuple[asyncio.Event, asyncio.Event],
    ) -> None:
        begin_event, finish_event = mock_message_bus_connect_events

        bus = Bus()

        async with asyncio.timeout(1):
            task = asyncio.create_task(bus.connect())

            try:
                await begin_event.wait()

                with pytest.raises(
                    RuntimeError, match='Cannot disconnect while a Bus lifecycle operation is in progress'
                ):
                    await bus.disconnect()

                finish_event.set()
                await task

                assert bus.connected is True
                assert bus.connecting is False
                assert bus.disconnecting is False

            finally:
                task.cancel()
                await asyncio.gather(task, return_exceptions=True)

            mock_message_bus.disconnect.assert_not_called()
            mock_message_bus.wait_for_disconnect.assert_not_awaited()

    @pytest.mark.parametrize('mock_message_bus_wait_for_disconnect_events', [True], indirect=True)
    async def test_disconnect_while_disconnecting(
        self,
        mock_message_bus: NonCallableMock,
        mock_message_bus_wait_for_disconnect_events: tuple[asyncio.Event, asyncio.Event],
    ) -> None:
        begin_event, finish_event = mock_message_bus_wait_for_disconnect_events

        bus = Bus()
        await bus.connect()

        async with asyncio.timeout(1):
            task = asyncio.create_task(bus.disconnect())

            try:
                await begin_event.wait()

                assert bus.connected is False
                assert bus.connecting is False
                assert bus.disconnecting is True

                with pytest.raises(
                    RuntimeError, match='Cannot disconnect while a Bus lifecycle operation is in progress'
                ):
                    await bus.disconnect()

                finish_event.set()
                await task

                assert bus.connected is False
                assert bus.connecting is False
                assert bus.disconnecting is False

            finally:
                finish_event.set()
                task.cancel()
                await asyncio.gather(task, return_exceptions=True)

        mock_message_bus.disconnect.assert_called_once_with()
        mock_message_bus.wait_for_disconnect.assert_awaited_once_with()

    @pytest.mark.parametrize('mock_message_bus_wait_for_disconnect_events', [True], indirect=True)
    async def test_disconnect_waits_for_cleanup_when_cancelled(
        self,
        mock_message_bus: NonCallableMock,
        mock_message_bus_wait_for_disconnect_events: tuple[asyncio.Event, asyncio.Event],
    ) -> None:
        begin_event, finish_event = mock_message_bus_wait_for_disconnect_events

        bus = Bus()
        await bus.connect()

        async with asyncio.timeout(1):
            task = asyncio.create_task(bus.disconnect())

            try:
                await begin_event.wait()
                task.cancel()

                # Wait one tick to ensure that the cancellation is processed and the disconnecting state is set.
                checkpoint = asyncio.Event()
                asyncio.get_running_loop().call_soon(checkpoint.set)
                await checkpoint.wait()

                assert not task.done()
                assert bus.disconnecting is True
                mock_message_bus.wait_for_disconnect.assert_awaited_once_with()

                finish_event.set()

                with pytest.raises(asyncio.CancelledError):
                    await task

                assert mock_message_bus.connected is False
                assert bus.connected is False
                assert bus.connecting is False
                assert bus.disconnecting is False

            finally:
                finish_event.set()
                task.cancel()
                await asyncio.gather(task, return_exceptions=True)

    @pytest.mark.parametrize(
        'mock_message_bus_request_name_reply',
        [RequestNameReply.PRIMARY_OWNER, RequestNameReply.ALREADY_OWNER],
        indirect=True,
    )
    async def test_request_name(self, mock_message_bus: NonCallableMock) -> None:
        bus = Bus()
        await bus.connect()

        name = 'com.example.TestService'

        await bus.request_name(name)
        mock_message_bus.request_name.assert_awaited_once_with(name, flags=NameFlag.DO_NOT_QUEUE)

    @pytest.mark.parametrize(
        'mock_message_bus_request_name_reply',
        [RequestNameReply.EXISTS, RequestNameReply.IN_QUEUE],
        indirect=True,
    )
    async def test_request_name_failed(
        self,
        mock_message_bus: NonCallableMock,
        mock_message_bus_request_name_reply: RequestNameReply,
    ) -> None:
        bus = Bus()
        await bus.connect()

        with pytest.raises(
            RuntimeError,
            match=f"Failed to acquire D-Bus name 'com.example.TestService': {mock_message_bus_request_name_reply.name}",
        ):
            await bus.request_name('com.example.TestService')

        mock_message_bus.request_name.assert_awaited_once_with('com.example.TestService', flags=NameFlag.DO_NOT_QUEUE)

    async def test_context_manager(self, mock_message_bus: NonCallableMock) -> None:
        async with Bus() as bus:
            assert bus.connected is True
            assert bus.connecting is False
            assert bus.disconnecting is False

        assert bus.connected is False
        assert bus.connecting is False
        assert bus.disconnecting is False

    async def test_request_name_not_connected(self, mock_message_bus: NonCallableMock) -> None:
        bus = Bus()

        with pytest.raises(RuntimeError, match='Bus is not connected'):
            await bus.request_name('com.example.TestService')

        mock_message_bus.request_name.assert_not_awaited()
