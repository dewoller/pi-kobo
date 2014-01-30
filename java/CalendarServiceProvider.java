package ca.wollersheim.dennis.keypad;


import android.annotation.TargetApi;
import android.content.Context;
import android.database.Cursor;
import android.net.Uri;
import android.util.Log;

@TargetApi(4)
public class CalendarServiceProvider {
	private final String LOG = "KeypadActivity";
	private final String calendarID = "2";
	private Context mContext;

	public CalendarServiceProvider(Context pContext) {
		mContext = pContext;
	}

	public void dumpCalendar() {
		Uri uri = getCalendarURI(false);
		Log.i(LOG, "Reading content from " + uri);
		readContent(uri);
		uri = getCalendarURI(true);
		Log.i(LOG, "Reading content from " + uri);
		readContent(uri);
	}

	private void readContent(Uri uri) {

		  Cursor cursor = mContext.getContentResolver().query(uri, null, null,
		    null, null);
		  if (cursor != null && cursor.getCount() > 0) {
		   cursor.moveToFirst();
		   String columnNames[] = cursor.getColumnNames();
		   String value = "";
		   String colNamesString = "";
		   do {
		    value = "";

		    for (String colName : columnNames) {
		     value += colName + " = ";
		     value += cursor.getString(cursor.getColumnIndex(colName))
		       + " ||";
		    }

		    Log.e("INFO : ", value);
		   } while (cursor.moveToNext());

		  }
	}
	
	
	
	private Uri getCalendarURI(boolean eventUri) {
		Uri calendarURI = null;

		if (android.os.Build.VERSION.SDK_INT <= 7) {
			calendarURI = (eventUri) ? Uri.parse("content://calendar/events")
					: Uri.parse("content://calendar/calendars");
		} else {
			calendarURI = (eventUri) 
					? 
						Uri.parse("content://com.android.calendar/events") 
					: 
						Uri.parse("content://com.android.calendar/calendars");
		}
		return calendarURI;
	}

	public String queryCalendar(String targetCode) {
		final String[] projection = {"title"};
		final String currtime = Long.toString(System.currentTimeMillis());
		final String[] selectionArgs = {currtime, currtime, targetCode, targetCode + " %"};
		final String selection = "dtstart < ? and dtend > ? and (title = ? or title like ?) ";
		
		Cursor cursor = mContext.getContentResolver().query(getCalendarURI(true), projection, selection, selectionArgs, null);
		String rv = null;
		if (cursor != null && cursor.getCount() > 0) {
			cursor.moveToFirst();
			do {
				String title = cursor.getString(cursor.getColumnIndex("title"));
				rv = title.substring(targetCode.length()+1);
				Log.e("INFO : Calendar contains ", title);
			} while (cursor.moveToNext() && rv != null);

		}
		return rv;
	}
}
