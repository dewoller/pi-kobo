import logging
import serial
import struct
import sys
import time


def sm130_checksum(packet):
  return sum(ord(x) for x in packet) % 256


def build_packet(command, payload):
  packet = struct.pack('BBB', 0x00, len(payload) + 1, command)
  packet += payload
  packet = '\xff' + packet + struct.pack('B', sm130_checksum(packet))
  return packet


def send_command(s, command, payload):
  logging.info("sending command %s, payload %s" % (command, payload))
  packet = build_packet(command, payload)
  s.write(packet)
  header, reserved, len, response_to = struct.unpack('BBBB', s.read(4))
  assert header == 0xFF
  assert reserved == 0x00
  response = s.read(len - 1)
  response_checksum = s.read(1)
  computed_checksum = build_packet(response_to, response)[-1]
  assert computed_checksum == response_checksum
  assert command == response_to
  return response

def main(args):
  rate = 19200
  s = serial.Serial(args[1], rate)
  # Give the module a chance to reset
  time.sleep(2)
  s.flushInput()
  logging.info("Version : %s", send_command(s, 0x81, ''))
  while True:
    logging.info("Tag : %s", send_command(s, 0x82, ''))
    time.sleep(2)


if __name__ == '__main__':
  logging.basicConfig(level=logging.DEBUG)
  main(sys.argv)
