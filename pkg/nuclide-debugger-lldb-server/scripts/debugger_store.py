# Copyright (c) 2015-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the LICENSE file in
# the root directory of this source tree.

import os
import re
from file_manager import FileManager
import serialize
from remote_objects import RemoteObjectManager
from thread_manager import ThreadManager
from logging_helper import log_debug


class DebuggerStore:
    '''Provides a central place for all debugger related managers.
    '''
    def __init__(self, debugger, chrome_channel, ipc_channel, is_attach, basepath='.'):
        '''
        chrome_channel: channel to send client chrome notification messages.
        ipc_channel: channel to send output/atom notification messages.
        debugger: lldb SBDebugger object.
        '''
        self._debugger = debugger
        self._chrome_channel = chrome_channel
        self._ipc_channel = ipc_channel
        self._is_attach = is_attach
        self._file_manager = FileManager(chrome_channel)
        self._remote_object_manager = RemoteObjectManager()
        basepath = self._resolve_basepath_heuristic(basepath)
        log_debug('basepath: %s' % basepath)
        self._location_serializer = serialize.LocationSerializer(
            self._file_manager, basepath)
        self._thread_manager = ThreadManager(self)

    def _resolve_basepath_heuristic(self, basepath):
        '''Buck emits relative path in the symbol file so we need a way to
        resolve all source from_filespec into absolute path.
        This heuristic will try to guess the buck root from executable module path.
        Note:
        This heuristic assumes user run buck built binaries directly from
        buck-out/gen sub-directories instead of being deployed to some other folder.
        Hopefully this is true most of the time.
        TODO: we need a better way to discover buck built root repo in long term.
        '''
        if basepath == '.':
            target = self._debugger.GetSelectedTarget()
            executable_dir_path = target.executable.GetDirectory()
            executable_dir_path = os.path.realpath(
                os.path.normpath(os.path.expanduser(executable_dir_path)))
            BUCK_OUTPUT_IDENTIFY_REGEX = '/buck-out/gen/'
            search_result = re.search(BUCK_OUTPUT_IDENTIFY_REGEX, executable_dir_path)
            if search_result:
                basepath = executable_dir_path[:search_result.start()]
        return basepath

    @property
    def chrome_channel(self):
        return self._chrome_channel

    @property
    def debugger(self):
        return self._debugger

    @property
    def ipc_channel(self):
        return self._ipc_channel

    @property
    def is_attach(self):
        return self._is_attach

    @property
    def thread_manager(self):
        return self._thread_manager

    @property
    def file_manager(self):
        return self._file_manager

    @property
    def remote_object_manager(self):
        return self._remote_object_manager

    @property
    def location_serializer(self):
        return self._location_serializer
