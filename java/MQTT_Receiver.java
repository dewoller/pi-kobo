package ca.wollersheim.dennis.keypad;

import java.util.Timer;
import java.util.TimerTask;

import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;
import org.eclipse.paho.client.mqttv3.MqttCallback;
import org.eclipse.paho.client.mqttv3.MqttClient;
import org.eclipse.paho.client.mqttv3.MqttClientPersistence;
import org.eclipse.paho.client.mqttv3.MqttDeliveryToken;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.eclipse.paho.client.mqttv3.MqttPersistenceException;
import org.eclipse.paho.client.mqttv3.MqttTopic;
import android.os.Environment;
import android.util.Log;

public class MQTT_Receiver implements MqttCallback {
	KeypadActivity parent;
	MqttClient client;
	MqttClientPersistence persist;
	private static MQTT_Receiver singleton;
	static final private long receptionMinimumInterval = 60;
	static final private String LOG = "KeypadActivity";
	private long timeLastMessage;
	int delay = 0; // no delay, start immediately
	int period = 70000;
	private long timeLastWifiReset = System.currentTimeMillis() / 1000l;
	int resetWifiSeconds = 600;
	Timer timer = new Timer();

	public MQTT_Receiver(KeypadActivity c) {
		parent = c;
		persist = new org.eclipse.paho.client.mqttv3.persist.MemoryPersistence();
		// persist = new MqttDefaultFilePersistence("/sdcard/persist");
		getNewClient();
		sendMessage("First starting");
		timer.scheduleAtFixedRate(new TimerTask() {
			public void run() {
				if (MQTT_Receiver.getInstance() != null)
					MQTT_Receiver.getInstance().checkAlive();
			}
		}, delay, period);
	}

	private void sendMessage(String s) {

		MqttMessage message = new MqttMessage(s.getBytes());
		message.setQos(0);
		try {
			if (client != null) {
				client.getTopic("keypad").publish(message);
			} else {
				getNewClient();
				client.getTopic("keypad").publish(message);
				}
		} catch (MqttPersistenceException e) {
			e.printStackTrace();
		} catch (MqttException e) {
			e.printStackTrace();
		}

	}

	public static MQTT_Receiver getInstance() {
		if (singleton != null)
			return singleton;
		return null;
	}

	public static MQTT_Receiver getInstance(KeypadActivity c) {
		if (singleton == null)
			singleton = new MQTT_Receiver(c);
		return singleton;
	}

	private void resetLastPing() {
		timeLastMessage = System.currentTimeMillis() / 1000l;
	}

	public void checkAlive() {
		long curtime = System.currentTimeMillis() / 1000l;
		// sendMessage("Checking For Life");
		if (curtime > timeLastMessage + receptionMinimumInterval) {
			Log.i(LOG, "connection Timed Out");
			getNewClient();
			sendMessage("Connection Timed Out");
		}
	}

	public void getNewClient() {
		try {
			if (client != null)
				try {
					client.disconnect();
				} catch (Exception e) {
					e.printStackTrace();
				}
			if (timeLastWifiReset > System.currentTimeMillis() / 1000l
					+ resetWifiSeconds) {
				parent.resetWIFI();
				try {
					Thread.sleep(10000);
				} catch (InterruptedException e) {
				}
				timeLastWifiReset = System.currentTimeMillis() / 1000l;
				sendMessage("Resetting Wifi");
			}
			resetLastPing();
			client = new MqttClient("tcp://192.168.1.31:1883",
					"KeypadUnlockListener", persist);
			client.connect();
			Thread.sleep(10000);
			client.subscribe("#");
			client.setCallback(this);
			sendMessage("Getting New Client");
		} catch (MqttException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			Log.i(LOG, e.getMessage());
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	@Override
	public void connectionLost(Throwable cause) {
		// TODO Auto-generated method stub
		Log.i(LOG, "lost Connection");
		getNewClient();

	}

	@Override
	public void messageArrived(String topic, MqttMessage message)
			throws Exception {
		// TODO Auto-generated method stub
		resetLastPing();
		String mess = message.toString();
		Log.i(LOG, "Topic:" + topic + ", Message: " + message);
		parent.processIncomingMQTTMessage(topic.toString(), message.toString());

	
		
	}

	@Override
	public void deliveryComplete(IMqttDeliveryToken token) {
		// TODO Auto-generated method stub
		
	}



}
