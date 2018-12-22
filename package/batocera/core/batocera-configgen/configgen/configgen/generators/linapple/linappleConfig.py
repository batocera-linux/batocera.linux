'''
Created on Mar 6, 2016

@author: Laurent Marchelli
'''
import os
import re
from Emulator import Emulator

joystick_translator = {
        # linapple : recalboxOS
        'Joy0Axis0' :   ('joystick1left', 'joystick2left', 'left'),
        'Joy0Axis1' :   ('joystick1up', 'joystick2up', 'up'),
        'Joy0Button1' : ('pagedown','x'),
        'Joy0Button2' : ('pageup', 'y'),
        'Joy1Axis0' :   ('joystick1left', 'joystick2left', 'left'),
        'Joy1Axis1':    ('joystick1up', 'joystick2up', 'up'),
        'Joy1Button1':  ('pagedown','x'),
        'JoyExitButton0' : ('select',),
        'JoyExitButton1' : ('start',)
    }

class LinappleConfig(object):
    '''
    Class managing linapple emulator configuration file.
    
    Customize the linappple configuration file (linapple.conf) with devices 
    informations provided by configgen classes.
    
    Args:
        filename (str):
            Configuration path and filename.
            
    '''
    def __init__(self, filename):
        self.load(filename)
    
    def load(self, filename=None):
        '''
        Load settings from the requested configuration file.
        
        Args:
            filename (str, None): 
                Configuration path and file name. 
                If None provided, self.filename is used.
        
        Returns (None):

        Notes:
            Commented and blank lines are stripped from the extraction.
        '''
        if filename:
            self.filename = filename
        else:
            filename = self.filename
        
        settings = {}
        patten = re.compile(r"^\s*(?P<name>\w+( \w+)*)\s*=" \
                            r"\s*(?P<value>[^\s]*).*$")
        with open(filename, 'r' ) as lines:
            for l in lines:
                m = patten.match(l)
                if m : settings[m.group('name')] = m.group('value')

        self.settings = settings
    
    def save(self, filename=None):
        '''
        Save all settings into a configuration file.
        
        Settings are written in alphabetical order in the configuration 
        file using the linapple parameters convention. 
        (see : Registry.cpp funct RegSaveKeyValue)
        
        Args:
            filename (str, None): 
                Configuration path and file name. 
                If None provided, self.filename is used.

        Returns (None):
        '''
        if filename:
            self.filename = filename
        else:
            filename = self.filename
        
        with open(filename, 'w') as file_out:
            for k, v in sorted(self.settings.items()):
                file_out.write('\t{}=\t{}\n'.format(k,v))

    def joysticks(self, controllers):
        '''
        Configure linapple joysticks (2) with given controllers.
        
        Args:
            controllers (dict):
                Dictionary of controllers connected (1 to 5).
        '''
        # Disable both joysticks
        self.settings['Joystick 0'] = '0'
        self.settings['Joystick 1'] = '0'
        
        # Configure axis and buttons for first two available joysticks
        joysticks = sorted(controllers.items())[:1]
        # Strange button behaviour with 2 joysticks enabled :-( TBD
        # joysticks = sorted(controllers.items())[:2] 
        for e, (n, c) in enumerate(joysticks):
            assert(n == c.player)   # Just if Controller source code changed
            
            # Use the translator to get recalbox value from linapple keyword 
            inputs = c.inputs
            joy_i = 'Joy{}'.format(e)
            transl = [(a, r) for (a, r) in joystick_translator.items() 
                      if a.startswith(joy_i)]
            for a, r in transl:
                value = None
                for i in r:
                    value = inputs.get(i, None)
                    if value is None: continue
                    if a.startswith(joy_i + 'Axis'):
                        if value.type != 'axis': continue
                    else:
                        if value.type != 'button': continue
                    break
                # If the input does not have the expected button we should
                # log the Error before exiting
                else: assert(False)
                self.settings[a] = value.id
            
            # Enable Joystick
            self.settings['Joy{}Index'.format(e)] = str(c.index)
            self.settings['Joystick {}'.format(e)] = '1'
            
        # Configure extended buttons informations
        if self.settings['Joystick 0'] == '1':
            inputs = joysticks[0][1].inputs
            for a in ('JoyExitButton0', 'JoyExitButton1'):
                for r in joystick_translator.get(a, ()):
                    value = inputs.get(r, None)
                    if value is not None and value.type == 'button': 
                        self.settings[a] = value.id
                        break
                else: self.settings[a] = ''
        
        jexit0 = self.settings['JoyExitButton0']        
        jexit1 = self.settings['JoyExitButton1']
        self.settings['JoyExitEnable'] ='1' if (jexit0 != '' and 
                                                jexit1 != '' and 
                                                jexit0 != jexit1) else '0'
    
    def system(self, system, filename):
        '''
        Configure Recalbox system settings
            
        Args:
            system (Emulator):
                Emulator object containing a config dictionay with all
                parameters set in EmulationStation.
            filename (str):
                Path and filename of the current disk.
        '''
        if filename:
            self.settings['Boot at Startup'] = '1'
            self.settings['Disk Image 1'] = filename
            self.settings['Slot 6 Autoload'] = '1'
        else:
            self.settings['Boot at Startup'] = '0'
            self.settings['Disk Image 1'] = ''
            self.settings['Slot 6 Autoload'] = '0'
        
        if filename and system.isOptSet('autosave') and system.getOptBoolean('autosave') == True:
            name = os.path.join(self.settings['Save State Directory'], 
                os.path.splitext(os.path.split(filename)[1])[0] + '.sve')
            self.settings['Save State Filename'] = name
            self.settings['Save State On Exit'] = '1'
        else:
            self.settings['Save State Filename'] = ''
            self.settings['Save State On Exit'] = '0'
    
        
# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
