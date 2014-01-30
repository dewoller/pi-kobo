package ca.wollersheim.dennis.keypad;


import ioio.lib.api.AnalogInput;
import ioio.lib.api.DigitalOutput;
import ioio.lib.api.exception.ConnectionLostException;
import ioio.lib.util.BaseIOIOLooper;
import android.content.Context;
import android.util.Log;

/**
 * An example IOIO service. While this service is alive, it will attempt to
 * connect to a IOIO and blink the LED. A notification will appear on the
 * notification bar, enabling the user to stop the service.
 */
public class KeypadIOIOLooper extends BaseIOIOLooper {
	private static KeypadIOIOLooper instance = null;
	private int[] temperaturePinID = {37,36,34,33 };
	private double[] tempMult = {1.0, 1.0, 1.0, 1.0};
	private int[] digitalOutputPinID = { 23, 22, 21, 20, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19 };
	private DigitalOutput[] digitalOutputPin = new DigitalOutput[digitalOutputPinID.length];
	private AnalogInput[] analogInputPin = new AnalogInput[temperaturePinID.length];
	private int analogBufferSize = 1000;
	private long[] pinStopTime = new long[digitalOutputPinID.length];
	private int lockIndex = 0;
	private boolean connected = false;
	public Exception IOIOError;
	private MQTT_Sender sender;


//	public enum IOIOError {
//		NONE, DISCONNECTED, INVALIDPIN, NEVERCONNECTED
//	};

	private final String LOG = "KeypadActivity";

	public KeypadIOIOLooper() {
		super();
		// create comm classes
		sender = new MQTT_Sender();
		sender.SendCommand("Starting IOIOLooper");
	}
	
	public static KeypadIOIOLooper getInstance() {
		if (instance == null ) {
			instance = new KeypadIOIOLooper();
		}
		return instance;
	}

	@Override
	protected void setup() throws ConnectionLostException {
		Log.d(LOG, "IOIO Setup");
		for (int i = 0; i < digitalOutputPin.length; i++) {
//			pin[i] = ioio_.openDigitalOutput(ioioPinID[i],
//					DigitalOutput.Spec.Mode.OPEN_DRAIN, true);
			digitalOutputPin[i] = ioio_.openDigitalOutput(digitalOutputPinID[i], true);
			pinStopTime[i] = 0;
		}
//		for (int i = 0; i < temperaturePinID.length; i++) {
//			analogInputPin[i] = ioio_.openAnalogInput(temperaturePinID[i]);
//			analogInputPin[i].setBuffer(analogBufferSize);
//		}
		connected = true;
	}
	public String readAllTemperature(int tempID) throws IOIOError {
		StringBuffer rv = new StringBuffer();
		if (tempID >= analogInputPin.length) 
			throw new IOIOError("Invalid Temperature Sensor;  I only have " + (analogInputPin.length) + " sensors");		
		try {
			int avail=analogInputPin[tempID].available();
			for (int i = 0; i<avail; i++)
				rv.append(',').append(analogInputPin[tempID].getVoltage()*100.0);
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			throw new IOIOError("Read interrupted");
		} catch (ConnectionLostException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			throw new IOIOError("Connection Lost");
		}
		
		return rv.toString();
	}
	public double readAverageTemperature(int tempID) throws IOIOError {
		double rv = 0;
		if (tempID >= analogInputPin.length) 
			throw new IOIOError("Invalid Temperature Sensor;  I only have " + (analogInputPin.length) + " sensors");		
		if (analogInputPin[tempID] == null )
			throw new IOIOError("Invalid Temperature Sensor; sensor not initialized");		
		try {
			analogInputPin[tempID] = ioio_.openAnalogInput(temperaturePinID[tempID]);
			analogInputPin[tempID].setBuffer(analogBufferSize);
			while( analogInputPin[tempID].available() < analogBufferSize) {
					Thread.sleep(100);
			}
			int avail=analogInputPin[tempID].available();
			for (int i = 0; i<avail; i++)
				rv += analogInputPin[tempID].getVoltage();
			rv = rv / avail *100.0 * tempMult[tempID];
			analogInputPin[tempID].close();
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			throw new IOIOError("Read interrupted");
		} catch (ConnectionLostException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			throw new IOIOError("Connection Lost");
		}
		
		return rv;
	}

	private boolean isLockPin( int switchID ) {
		return switchID==lockIndex;
	}
	public void unlockDoor() throws IOIOError {
		Log.d(LOG, "Unlocking");
		setPin(lockIndex, 8);
	}

	public void safeSetPin(int switchID, int seconds) throws IOIOError {
		if (isLockPin(switchID)) 
			throw new IOIOError("Invalid Pin");
		setPin(switchID, seconds);
	}
	
	private void setPin(int switchID, int seconds) throws IOIOError {
		// sanity checking
		if (!connected || digitalOutputPin[0]==null)
			throw new IOIOError("Never Connected");
		if (switchID >= pinStopTime.length ) {
			throw new IOIOError("Invalid Pin");
		}
		pinStopTime[switchID] = System.currentTimeMillis() + seconds * 1000;
		try {
			setPin(switchID);
		} catch (ConnectionLostException e) {
			// TODO Auto-generated catch block
			// showToastFromBackground("lost connection");
			throw new IOIOError("Disconnected");
		}
	}

	
	private void setPin(int switchID) throws ConnectionLostException {
		digitalOutputPin[switchID].write(false);
	}

	private void unsetPin(int switchID) throws ConnectionLostException {
		Log.d(LOG, "Unsetting Pin " + switchID);
		digitalOutputPin[switchID].write(true);
	}

	public void resetAllPins() {
		try {
			for (int i = 0; i < digitalOutputPin.length; i++) {
				if ( digitalOutputPin[i]!= null)
					digitalOutputPin[i].write(true) ;
				pinStopTime[i] = 0;
			}
		} catch (ConnectionLostException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			Log.e(LOG, e.getMessage());
		}
	}

	protected void processPinStopEvents() throws ConnectionLostException {
		long currSec = System.currentTimeMillis();
		for (int i = 0; i < digitalOutputPin.length; i++) {
			if (pinStopTime[i] > 0 && currSec > pinStopTime[i]) {
				pinStopTime[i] = 0;
				unsetPin(i);
			}
		}
	}
	
	protected void water(int pin, int wateringDuration) {
			try {
				safeSetPin(pin, wateringDuration);
			} catch (IOIOError e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		Log.d(LOG, "SetPin " + pin + ", duration " + wateringDuration);
		sender.SendCommand("Tried to started watering for " + wateringDuration
				+ " seconds");
	}

	/**
	 * Called repetitively while the IOIO is connected.
	 * 
	 * @throws ConnectionLostException
	 *             When IOIO connection is lost.
	 * 
	 * @see ioio.lib.util.AbstractIOIOActivity.IOIOThread#loop()
	 */
	@Override
	public void loop() throws ConnectionLostException {
		// here, we respond to IOIO events; keypad events are handled
		// elsewhere
		processPinStopEvents();
		try {
			Thread.sleep(100);
		} catch (InterruptedException e) {
		}
	}
	

	
}
