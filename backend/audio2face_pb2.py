# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: audio2face.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10\x61udio2face.proto\x12\x11nvidia.audio2face\"{\n\x10PushAudioRequest\x12\x15\n\rinstance_name\x18\x01 \x01(\t\x12\x12\n\nsamplerate\x18\x02 \x01(\x05\x12\x12\n\naudio_data\x18\x03 \x01(\x0c\x12(\n block_until_playback_is_finished\x18\x04 \x01(\x08\"5\n\x11PushAudioResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\"\x85\x01\n\x16PushAudioStreamRequest\x12@\n\x0cstart_marker\x18\x01 \x01(\x0b\x32(.nvidia.audio2face.PushAudioRequestStartH\x00\x12\x14\n\naudio_data\x18\x02 \x01(\x0cH\x00\x42\x13\n\x11streaming_request\"l\n\x15PushAudioRequestStart\x12\x15\n\rinstance_name\x18\x01 \x01(\t\x12\x12\n\nsamplerate\x18\x02 \x01(\x05\x12(\n block_until_playback_is_finished\x18\x03 \x01(\x08\";\n\x17PushAudioStreamResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t2\xd4\x01\n\nAudio2Face\x12X\n\tPushAudio\x12#.nvidia.audio2face.PushAudioRequest\x1a$.nvidia.audio2face.PushAudioResponse\"\x00\x12l\n\x0fPushAudioStream\x12).nvidia.audio2face.PushAudioStreamRequest\x1a*.nvidia.audio2face.PushAudioStreamResponse\"\x00(\x01\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'audio2face_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_PUSHAUDIOREQUEST']._serialized_start=39
  _globals['_PUSHAUDIOREQUEST']._serialized_end=162
  _globals['_PUSHAUDIORESPONSE']._serialized_start=164
  _globals['_PUSHAUDIORESPONSE']._serialized_end=217
  _globals['_PUSHAUDIOSTREAMREQUEST']._serialized_start=220
  _globals['_PUSHAUDIOSTREAMREQUEST']._serialized_end=353
  _globals['_PUSHAUDIOREQUESTSTART']._serialized_start=355
  _globals['_PUSHAUDIOREQUESTSTART']._serialized_end=463
  _globals['_PUSHAUDIOSTREAMRESPONSE']._serialized_start=465
  _globals['_PUSHAUDIOSTREAMRESPONSE']._serialized_end=524
  _globals['_AUDIO2FACE']._serialized_start=527
  _globals['_AUDIO2FACE']._serialized_end=739
# @@protoc_insertion_point(module_scope)
