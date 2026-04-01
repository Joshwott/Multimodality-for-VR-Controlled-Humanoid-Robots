using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Net.Sockets;
using System.Text;
using UnityEngine.XR;

/*
* Class for tracking the Meat Quest 2 Headset and sending it across a UDP Connection.
*/
public class ControllerTracker : MonoBehaviour
{
    public Transform headAnchor;
    public Transform leftAnchor;
    public Transform rightAnchor;
    private InputDevice rightController;

    UdpClient client;
    string address = "10.138.161.31";
    int port = 5005;

    /*
    * Method that runs on start up of the unity app and gets the details of the VR Headset.
    * Connects to the UDP Server hosted on the python script as a client.
    */
    void Start()
    {
        client = new UdpClient();

        List<InputDevice> devices = new List<InputDevice>();
        InputDevices.GetDevicesAtXRNode(XRNode.RightHand, devices);
        if (devices.Count > 0)
        {
            rightController = devices[0];
            Debug.Log("Right controller found:" + rightController.name);
        }
    }

    /*
    * Method updates every frame and returns telemetry data of the Headset.
    * The data tracked is put into a byte array and then sent via the UDP Connection to the python script.
    */
    void Update()
    {
        if (leftAnchor != null || rightAnchor != null)
        {
            Vector3 headPosition = headAnchor.position;
            Vector3 headRotation = headAnchor.eulerAngles;

            Vector3 leftControllerPosition = leftAnchor.position;
            Vector3 rightControllerPosition = rightAnchor.position;

            Vector3 leftcontrollerRotation = leftAnchor.eulerAngles;
            Vector3 rightControllerRotation = rightAnchor.eulerAngles;

            Vector2 rightJoystick = Vector2.zero;
            if (rightController.isValid)
            {
                rightController.TryGetFeatureValue(CommonUsages.primary2DAxis, out rightJoystick);
            }

            string data = 
                  leftControllerPosition.x + "," + leftControllerPosition.y + "," + leftControllerPosition.z +
            "|" + rightControllerPosition.x + "," + rightControllerPosition.y + "," + rightControllerPosition.z +
            "|" + rightJoystick.x + "," + rightJoystick.y +
            "|" + leftcontrollerRotation.x + "," + leftcontrollerRotation.y + "," + leftcontrollerRotation.z +
            "|" + rightControllerRotation.x + "," + rightControllerRotation.y + "," + rightControllerRotation.z +
            "|" + headPosition.x + "," + headPosition.y + "," + headPosition.z +
            "|" + headRotation.x + "," + headRotation.y + "," + headRotation.z;

            byte[] payload = Encoding.UTF8.GetBytes(data);
            client.Send(payload, payload.Length, address, port);
        }
    }
}
