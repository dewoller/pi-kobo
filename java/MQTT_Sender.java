/*
 * Copyright (C) 2010 Thomas G. Kenny Jr
 *
 * Licensed under the GNU General Public License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at 
 *
 *      http://www.gnu.org/licenses/old-licenses/gpl-2.0.html
 *
 * Unless required by applicable law or agreed to in writing, software 
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and 
 * limitations under the License.
 */

package ca.wollersheim.dennis.keypad;

import org.eclipse.paho.client.mqttv3.MqttClient;

import org.eclipse.paho.client.mqttv3.MqttClientPersistence;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence;
import org.eclipse.paho.client.mqttv3.persist.MqttDefaultFilePersistence;

import android.util.Log;

/** Class that handles network communication **/
public class MQTT_Sender {
	MqttClient client;
	private static final String keypadTopic = "keypad";
	private static final String LOG = "KeypadActivity";

	/** Parent activity is used to get context */
	public MQTT_Sender() {

	}

	/**
	 * Connects to the given address and port. Any existing connection will be
	 * broken first
	 **/
	public void Connect() {
 
	}

	/** Closes the socket if it exists and it is already connected **/
	public void Disconnect() {

	}

	public void SendCommand(String cmd) {
		// send command data
		try {
			Log.i(LOG, "Sending MQTT string " + cmd);

			MqttClientPersistence persist = new MqttDefaultFilePersistence("/sdcard/temp");
			client = new MqttClient("tcp://192.168.1.31:1883", "Keypad", persist);
			client.connect();
			MqttMessage message = new MqttMessage(cmd.getBytes());
			message.setQos(0);
			client.getTopic(keypadTopic).publish(message);
			client.disconnect();
		} catch (MqttException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			Log.e(LOG, e.getMessage());
		}
	}

}
