# Trace Snow Converting Script

Trace Snow was a ski/snowboard tracking app, but
is no longer available. The web server is also down
so there is no way to sync the data.

This script helps converting the GPS data stored by Trace Snow into common GPX file so we can import the previous tracks into other
ski/snowboarding app, e.g. Slopes.

## When to use

The following steps applied when:

1. You were using an Android device (for ios I'm not sure
   how to get the database) for Trace Snow.
2. Trace Snow app was installed, with trace list sync'ed. I.e.,
   you can see you trip list (It's OK if you cannot see the full track)


## Usage

1. Enable USB debug for your Android device. https://developer.android.com/studio/debug/dev-options#Enable-debugging
2. Download the trip list database.
   ```(shell)
   adb pull /storage/emulated/0/Android/data/com.alpinereplay.android/files
   ```
3. List your trip data by sqlite
   ```(shell)
   sqlite3 example.sqlite
   sqlite> select location_name,track_url from visits;
   ```

   You should be able to see data like:
   ```
   abc resort|https://s3.amazonaws.com/alpinereplay/public/users/702000/702773/visits/37955213/visit.trk
   ```

   The URL s3.amazonaws.com/.../visit.trk is the GPS data. You can paste
   this URL to browser to download the .trk file.
4. Run the python script to convert the .trk file into .gpx format.
   ```
   ./trk.py --input visit.trk --tz <timezone_hour_diff_from_UTC> --name <trip_name>
   ```