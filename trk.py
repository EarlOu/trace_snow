#!/usr/bin/env python3

import argparse
import base64
import bitstring
import datetime
import json
import os

import gpxpy
import gpxpy.gpx


def parse_freq(segment):
  return [int(segment['base']) + i * segment['step'] for i in range(segment['size'])]


def parse_base64(segment):
  assert segment['signed']
  data = base64.b64decode(segment['data'])
  factor = segment['factor']
  bitwidth = segment['bitwidth']
  base = segment['base']
  bs = bitstring.Bits(data)
  res = [base]
  for value in bs.cut(bitwidth):
    res.append(value.int * factor + res[-1])
  return res


def parse_segment(segments):
  res = []
  for segment in segments:
    if segment['encoding'] == 'freq':
      res += parse_freq(segment)
    elif segment['encoding'] == 'base64/diff':
      res += parse_base64(segment)
    else:
      assert False
  return res


def parse_series(series, tz):
  size = series['size']

  alt = parse_segment(series['data']['alt']['segments'])
  time = parse_segment(series['data']['time']['segments'])
  lon = parse_segment(series['data']['lon']['segments'])
  lat = parse_segment(series['data']['lat']['segments'])
  speed = parse_segment(series['data']['speed']['segments'])

  assert size == len(time)
  assert size == len(lon)
  assert size == len(lat)
  assert size == len(alt)
  assert size == len(speed)

  gpx_segment = gpxpy.gpx.GPXTrackSegment()
  for i in range(size):
    gpx_segment.points.append(
        gpxpy.gpx.GPXTrackPoint(
            latitude = lat[i],
            longitude = lon[i],
            elevation = alt[i],
            speed = speed[i],
            time = datetime.datetime.fromtimestamp(time[i],
                                                   tz=datetime.timezone(datetime.timedelta(hours=tz))),
            horizontal_dilution = 0,
            vertical_dilution = 0,
        ))

  return gpx_segment


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument(
      "--input", type=str)
  parser.add_argument(
      "--tz", type=int)
  parser.add_argument(
      "--name", type=str)
  args = parser.parse_args()

  with open(args.input, "r") as ifile:
    data = ifile.read()

  data = data[13:-1]
  json_data = json.loads(data)

  gpx = gpxpy.gpx.GPX()
  gpx_track = gpxpy.gpx.GPXTrack()
  gpx_track.name = args.name
  gpx.tracks.append(gpx_track)

  for key, series in json_data.items():
    gpx_track.segments.append(parse_series(series, args.tz))


  with open(os.path.splitext(args.input)[0] + ".gpx", "w") as ofile:
    ofile.write(gpx.to_xml())

main()