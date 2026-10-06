from __future__ import annotations

import asyncio
import threading
from contextlib import asynccontextmanager, suppress
from dataclasses import dataclass, field
from importlib.metadata import EntryPoint
from typing import TYPE_CHECKING

import pytest

from batocera_launch.plugin_manager import HookContext, Plugin, PluginManager

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Awaitable, Callable, Iterator
    from unittest.mock import Mock

    from pytest_mock import MockerFixture


@pytest.fixture
def context(mocker: MockerFixture) -> HookContext:
    return HookContext(config=mocker.Mock())


@pytest.fixture
def mock_plugin_1(mocker: MockerFixture) -> Mock:
    return mocker.Mock(spec=Plugin)


@pytest.fixture
def mock_entry_point_1(mocker: MockerFixture, mock_plugin_1: Mock) -> Mock:
    entry_point = mocker.Mock(spec=EntryPoint)
    entry_point.name = 'mock_plugin_1'
    entry_point.load.return_value = mocker.Mock(return_value=mock_plugin_1)
    return entry_point


@pytest.fixture
def mock_plugin_2(mocker: MockerFixture) -> Mock:
    return mocker.Mock(spec=Plugin)


@pytest.fixture
def mock_entry_point_2(mocker: MockerFixture, mock_plugin_2: Mock) -> Mock:
    entry_point = mocker.Mock(spec=EntryPoint)
    entry_point.name = 'mock_plugin_2'
    entry_point.load.return_value = mocker.Mock(return_value=mock_plugin_2)
    return entry_point


@pytest.fixture(autouse=True)
def mock_entry_points(mocker: MockerFixture, mock_entry_point_1: Mock, mock_entry_point_2: Mock) -> Mock:
    return mocker.patch(
        'batocera_launch.plugin_manager.entry_points',
        return_value=[mock_entry_point_1, mock_entry_point_2],
    )


@pytest.fixture
def manager(context: HookContext) -> PluginManager:
    return PluginManager(context)


@dataclass
class _HookGate:
    entered: asyncio.Event = field(default_factory=asyncio.Event)
    completed: asyncio.Event = field(default_factory=asyncio.Event)
    release: threading.Event = field(default_factory=threading.Event)


@pytest.fixture
def block_hook() -> Iterator[Callable[[Mock], _HookGate]]:
    gates: list[_HookGate] = []

    def block(hook: Mock) -> _HookGate:
        loop = asyncio.get_running_loop()
        gate = _HookGate()
        gates.append(gate)

        def call(context: HookContext) -> None:
            loop.call_soon_threadsafe(gate.entered.set)
            try:
                # A deadline prevents a failing test from stranding a worker thread.
                if not gate.release.wait(timeout=10):
                    raise TimeoutError('test did not release the plugin hook')
            finally:
                loop.call_soon_threadsafe(gate.completed.set)

        hook.side_effect = call
        return gate

    yield block

    for gate in gates:
        gate.release.set()


@asynccontextmanager
async def _waiting(operation: Callable[[], Awaitable[None]]) -> AsyncGenerator[asyncio.Task[None]]:
    """Run a public lifecycle operation and wait until it has started awaiting."""
    entered = asyncio.Event()

    async def run() -> None:
        entered.set()
        await operation()

    task = asyncio.create_task(run())
    try:
        await entered.wait()
        yield task
    finally:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task


class TestPluginManager:
    def test_plugins_are_loaded(
        self, manager: PluginManager, mock_entry_points: Mock, mock_plugin_1: Mock, mock_plugin_2: Mock
    ) -> None:
        mock_entry_points.assert_called_once_with(group='batocera_launch.plugins')
        assert manager.plugins == [mock_plugin_1, mock_plugin_2]
        mock_plugin_1.start.assert_not_called()
        mock_plugin_2.start.assert_not_called()
        mock_plugin_1.stop.assert_not_called()
        mock_plugin_2.stop.assert_not_called()

    @pytest.mark.parametrize('failure_stage', ['load', 'construction'])
    @pytest.mark.parametrize('failed_entry_point', ['mock_entry_point_1', 'mock_entry_point_2'])
    def test_failed_plugin_is_logged_and_other_plugins_are_loaded(
        self,
        caplog: pytest.LogCaptureFixture,
        context: HookContext,
        request: pytest.FixtureRequest,
        mock_plugin_1: Mock,
        mock_plugin_2: Mock,
        failure_stage: str,
        failed_entry_point: str,
    ) -> None:
        entry_point = request.getfixturevalue(failed_entry_point)
        error = RuntimeError('plugin unavailable')
        if failure_stage == 'load':
            entry_point.load.side_effect = error
        else:
            entry_point.load.return_value.side_effect = error

        with caplog.at_level('ERROR'):
            manager = PluginManager(context)

        healthy_plugin = mock_plugin_2 if failed_entry_point == 'mock_entry_point_1' else mock_plugin_1
        assert manager.plugins == [healthy_plugin]
        assert f'cannot load plugin {entry_point.name}' in caplog.text
        assert any(record.exc_info and record.exc_info[1] is error for record in caplog.records)

    @pytest.mark.parametrize('no_plugins', ['none_registered', 'all_fail'])
    async def test_lifecycle_without_plugins(
        self,
        context: HookContext,
        mock_entry_points: Mock,
        mock_entry_point_1: Mock,
        mock_entry_point_2: Mock,
        no_plugins: str,
    ) -> None:
        if no_plugins == 'none_registered':
            mock_entry_points.return_value = []
        else:
            mock_entry_point_1.load.side_effect = ImportError('unavailable')
            mock_entry_point_2.load.side_effect = ImportError('unavailable')
        manager = PluginManager(context)

        await manager.ready()
        manager.start()
        await manager.ready()
        await manager.stop()

        assert manager.plugins == []

    async def test_hooks_receive_context_once_in_lifecycle_order(
        self, manager: PluginManager, context: HookContext, mock_plugin_1: Mock, mock_plugin_2: Mock
    ) -> None:
        manager.start()
        await manager.ready()
        await manager.ready()

        for plugin in (mock_plugin_1, mock_plugin_2):
            plugin.start.assert_called_once_with(context)
            plugin.stop.assert_not_called()

        await manager.stop()

        for plugin in (mock_plugin_1, mock_plugin_2):
            plugin.start.assert_called_once_with(context)
            plugin.stop.assert_called_once_with(context)

    async def test_ready_before_start_does_not_invoke_hooks(
        self, manager: PluginManager, mock_plugin_1: Mock, mock_plugin_2: Mock
    ) -> None:
        await manager.ready()

        for plugin in (mock_plugin_1, mock_plugin_2):
            plugin.start.assert_not_called()
            plugin.stop.assert_not_called()

    async def test_stop_without_start(
        self, manager: PluginManager, context: HookContext, mock_plugin_1: Mock, mock_plugin_2: Mock
    ) -> None:
        await manager.stop()

        for plugin in (mock_plugin_1, mock_plugin_2):
            plugin.start.assert_not_called()
            plugin.stop.assert_called_once_with(context)

    async def test_default_plugin_hooks_are_optional(
        self, context: HookContext, mock_entry_point_1: Mock, mock_entry_points: Mock
    ) -> None:
        mock_entry_point_1.load.return_value = Plugin
        mock_entry_points.return_value = [mock_entry_point_1]
        manager = PluginManager(context)

        manager.start()
        await manager.ready()
        await manager.stop()

    @pytest.mark.parametrize('hook_name', ['start', 'stop'])
    @pytest.mark.parametrize('failed_plugin', ['mock_plugin_1', 'mock_plugin_2'])
    async def test_hook_failure_is_logged_and_does_not_prevent_other_hooks(
        self,
        manager: PluginManager,
        context: HookContext,
        caplog: pytest.LogCaptureFixture,
        request: pytest.FixtureRequest,
        mock_plugin_1: Mock,
        mock_plugin_2: Mock,
        hook_name: str,
        failed_plugin: str,
    ) -> None:
        plugin = request.getfixturevalue(failed_plugin)
        error = RuntimeError('hook failed')
        getattr(plugin, hook_name).side_effect = error

        with caplog.at_level('ERROR'):
            manager.start()
            await manager.ready()
            await manager.stop()

        for plugin in (mock_plugin_1, mock_plugin_2):
            plugin.start.assert_called_once_with(context)
            plugin.stop.assert_called_once_with(context)
        assert f'failed on {hook_name}' in caplog.text
        assert any(record.exc_info and record.exc_info[1] is error for record in caplog.records)

    @pytest.mark.parametrize('hook_name', ['start', 'stop'])
    async def test_hooks_run_concurrently_without_blocking_the_event_loop(
        self,
        manager: PluginManager,
        mock_plugin_1: Mock,
        mock_plugin_2: Mock,
        block_hook: Callable[[Mock], _HookGate],
        hook_name: str,
    ) -> None:
        first = block_hook(getattr(mock_plugin_1, hook_name))
        second = block_hook(getattr(mock_plugin_2, hook_name))
        manager.start()
        operation = manager.ready if hook_name == 'start' else manager.stop

        async with _waiting(operation) as waiting:
            try:
                # Both hooks must enter before either is released. Reaching here also
                # demonstrates that a blocked synchronous hook leaves the loop responsive.
                await asyncio.wait_for(first.entered.wait(), timeout=5)
                await asyncio.wait_for(second.entered.wait(), timeout=5)
                assert not waiting.done()

                first.release.set()
                await asyncio.wait_for(first.completed.wait(), timeout=5)
                assert not waiting.done()
            finally:
                first.release.set()
                second.release.set()
            await asyncio.wait_for(waiting, timeout=5)

    async def test_stop_waits_for_every_start_without_an_explicit_ready(
        self,
        manager: PluginManager,
        context: HookContext,
        mock_plugin_1: Mock,
        mock_plugin_2: Mock,
        block_hook: Callable[[Mock], _HookGate],
    ) -> None:
        first = block_hook(mock_plugin_1.start)
        second = block_hook(mock_plugin_2.start)
        manager.start()

        async with _waiting(manager.stop) as stopping:
            try:
                await asyncio.wait_for(first.entered.wait(), timeout=5)
                await asyncio.wait_for(second.entered.wait(), timeout=5)
                first.release.set()
                await asyncio.wait_for(first.completed.wait(), timeout=5)

                assert not stopping.done()
                mock_plugin_1.stop.assert_not_called()
                mock_plugin_2.stop.assert_not_called()
            finally:
                first.release.set()
                second.release.set()
            await asyncio.wait_for(stopping, timeout=5)

        mock_plugin_1.stop.assert_called_once_with(context)
        mock_plugin_2.stop.assert_called_once_with(context)

    @pytest.mark.parametrize('cancelled_operation', ['ready', 'stop'])
    async def test_cancelling_a_waiter_preserves_startup_and_later_shutdown(
        self,
        manager: PluginManager,
        context: HookContext,
        mock_plugin_1: Mock,
        mock_plugin_2: Mock,
        block_hook: Callable[[Mock], _HookGate],
        cancelled_operation: str,
    ) -> None:
        gate = block_hook(mock_plugin_1.start)
        manager.start()

        async with _waiting(getattr(manager, cancelled_operation)) as waiting:
            await asyncio.wait_for(gate.entered.wait(), timeout=5)
            waiting.cancel()
            with pytest.raises(asyncio.CancelledError):
                await waiting

        async with _waiting(manager.stop) as stopping:
            try:
                assert not stopping.done()
                mock_plugin_1.stop.assert_not_called()
                mock_plugin_2.stop.assert_not_called()
            finally:
                gate.release.set()
            await asyncio.wait_for(stopping, timeout=5)

        assert gate.completed.is_set()
        mock_plugin_1.start.assert_called_once_with(context)
        mock_plugin_2.start.assert_called_once_with(context)
        mock_plugin_1.stop.assert_called_once_with(context)
        mock_plugin_2.stop.assert_called_once_with(context)

    async def test_cancelling_one_ready_waiter_does_not_cancel_another(
        self,
        manager: PluginManager,
        context: HookContext,
        mock_plugin_1: Mock,
        mock_plugin_2: Mock,
        block_hook: Callable[[Mock], _HookGate],
    ) -> None:
        gate = block_hook(mock_plugin_1.start)
        manager.start()

        async with _waiting(manager.ready) as first, _waiting(manager.ready) as second:
            try:
                await asyncio.wait_for(gate.entered.wait(), timeout=5)
                first.cancel()
                with pytest.raises(asyncio.CancelledError):
                    await first

                assert not second.done()
            finally:
                gate.release.set()
            await asyncio.wait_for(second, timeout=5)

        await manager.stop()
        mock_plugin_1.start.assert_called_once_with(context)
        mock_plugin_2.start.assert_called_once_with(context)
        mock_plugin_1.stop.assert_called_once_with(context)
        mock_plugin_2.stop.assert_called_once_with(context)
