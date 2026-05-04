using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Net.Sockets;
using System.Text;
using UnityEngine.XR;
using System.Net;

/*
* Class for tracking the Meat Quest 2 Headset and sending it across a UDP Connection.
*/
public class ControllerTracker : MonoBehaviour
{
    public Transform headAnchor;
    public Transform leftAnchor;
    public Transform rightAnchor;
    public string address = "10.138.161.23";
    public int sendPort = 5005;
    public IPEndPoint anyIP;
    public int receivePort = 5010;
    private float minXLeft;
    private float maxXLeft;
    private float minXRight;
    private float maxXRight;
    private float minY;
    private float maxY;
    private float minZ;
    private float maxZ;
    private InputDevice rightController;
    private InputDevice leftController;
    bool calibrationReceived = false;
    UdpClient client;
    UdpClient receiveClient;

    readonly Dictionary<string, Vector2> leftLimits = new Dictionary<string, Vector2>()
    {
        {"ShoulderPitch", new Vector2(-2.0f, 2.0f)},
        {"ShoulderRoll", new Vector2(0.0f, 1.5f)},
    };

    readonly Dictionary<string, Vector2> rightLimits = new Dictionary<string, Vector2>()
    {
        {"ShoulderPitch", new Vector2(-2.0f, 2.0f)},
        {"ShoulderRoll", new Vector2(-1.5f, 0.0f)},
    };

    /*
    * Method that runs on start up of the unity app and gets the details of the VR Headset.
    * Connects to the UDP Server hosted on the python script as a client.
    */
    void Start()
    {       
        client = new UdpClient();

        List<InputDevice> rightDevices = new List<InputDevice>();
        InputDevices.GetDevicesAtXRNode(XRNode.RightHand, rightDevices);
        if (rightDevices.Count > 0)
        {
            rightController = rightDevices[0];
            Debug.Log("Right controller found:" + rightController.name);
        }

        List<InputDevice> leftDevices = new List<InputDevice>();
        InputDevices.GetDevicesAtXRNode(XRNode.LeftHand, leftDevices);
        if (leftDevices.Count > 0)
        {
            leftController = leftDevices[0];
            Debug.Log("Left controller found:" + leftController.name);
        }

        receiveClient = new UdpClient(receivePort);
        anyIP = new IPEndPoint(System.Net.IPAddress.Any, 0);

        Debug.Log("Listening for Calibration data on port " + receivePort);

    }

    /*
    * Method updates every frame and returns telemetry data of the Headset.
    * The data tracked is put into a byte array and then sent via the UDP Connection to the python script.
    */
    void Update()
    {
        if (receiveClient.Available > 0)
        {
            byte[] data = receiveClient.Receive(ref anyIP);
            string message = Encoding.UTF8.GetString(data);

            Debug.Log("Calibration Received: " + message);

            if (message.StartsWith("CalibrationData|"))
            {
                string[] values = message.Substring("CalibrationData|".Length).Split(',');

                minXLeft  = float.Parse(values[0]);
                maxXLeft  = float.Parse(values[1]);
                minXRight = float.Parse(values[2]);
                maxXRight = float.Parse(values[3]);
                minY = float.Parse(values[4]);
                maxY = float.Parse(values[5]);
                minZ = float.Parse(values[6]);
                maxZ = float.Parse(values[7]);

                calibrationReceived = true;
            }
        }

        if (leftAnchor != null && rightAnchor != null)
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
            client.Send(payload, payload.Length, address, sendPort);  

            if (calibrationReceived)
            {
                Vector3 leftPositionNorm = new Vector3(
                    Normalise(leftAnchor.position.x, minXLeft, maxXLeft),
                    Normalise(leftAnchor.position.y, minY, maxY),
                    Normalise(leftAnchor.position.z, minZ, maxZ));

                Vector3 rightPositionNorm = new Vector3(
                    Normalise(rightAnchor.position.x, minXRight, maxXRight),
                    Normalise(rightAnchor.position.y, minY, maxY),
                    Normalise(rightAnchor.position.z, minZ, maxZ));

                NAOLimitHapticFeedback(leftPositionNorm, leftController, false);
                NAOLimitHapticFeedback(rightPositionNorm, rightController, true);
            }
        }

        /*
        * Triggers the haptic feedback in the relevant controller based on the calculated values.
        * @param position 
        */
        void NAOLimitHapticFeedback(Vector3 position, InputDevice controller, bool isRight)
        {
            if (!controller.isValid)
            {
                return;
            }

            Vector2 angles = GetArmAngles(position, isRight);
            Dictionary<string, Vector2> limits;
            if (isRight)
            {
                limits = rightLimits;
            }
            else
            {
                limits = leftLimits;
            }

            float pitchIntensity = GetLimitIntensity(angles.x, limits["ShoulderPitch"]);
            float rollIntensity = GetLimitIntensity(angles.y, limits["ShoulderRoll"]);
            float intensity = Mathf.Max(pitchIntensity, rollIntensity);

            bool clamped = IsClamped(angles.x, limits["ShoulderPitch"]) ||
                IsClamped(angles.y, limits["ShoulderRoll"]);

            if (clamped)
            {
                controller.SendHapticImpulse(0, 1.0f, 0.12f);
            }

            else if (intensity > 0.05f)
            {
                controller.SendHapticImpulse(0, intensity * 0.5f, 0.05f);
            }
        }

        /*
        * Nomralises the values input.
        * @param value current value.
        * @param min smallest allowed value.
        * @param max largest allowed value.
        */
        float Normalise(float value, float min, float max)
        {
            if (Mathf.Abs(max - min) < 0.0001f) return 0.5f;
            return Mathf.Clamp01((value - min) / (max - min));
        }

        /*
        * Gets the angles of the arms based of the position and limts in the dictionaries.
        * @param position within the 3D space.
        * @param isRight checks to see if the current controller data is from the left or right.
        * @return 2DVector containing the pitch and roll of the shoulder.
        */
        Vector2 GetArmAngles(Vector3 position, bool isRight)
        {
            float xNorm = position.x;
            float yNorm = position.y;

            if (isRight)
                xNorm = 1 - xNorm;

            Dictionary<string, Vector2> limits = isRight ? rightLimits : leftLimits;

            float shoulderPitch = (1 - yNorm) * (limits["ShoulderPitch"].y - limits["ShoulderPitch"].x)
                                + limits["ShoulderPitch"].x;

            float rollNorm = isRight ? xNorm : (1 - xNorm);
            float shoulderRoll = rollNorm * (limits["ShoulderRoll"].y - limits["ShoulderRoll"].x)
                                + limits["ShoulderRoll"].x;

            return new Vector2(shoulderPitch, shoulderRoll);
        }

        /*
        * Method that gradual scales the intesnsity of the haptics depending on the distance from the
        *  boundry.
        * @param value current value.
        * @param limits the allowed values min and max.
        * @param threshold of when the vibration begins
        * @return intensity the clamped intensity value.
        */
        float GetLimitIntensity(float value, Vector2 limits, float threshold = 0.2f)
        {
            float distToMin = Mathf.Abs(value - limits.x);
            float distToMax = Mathf.Abs(limits.y - value);

            float intensity = 0f;

            if (distToMin < threshold)
            {
                intensity = Mathf.Max(intensity, 1 - (distToMin / threshold));
            }
            if (distToMax < threshold)
            {
                intensity = Mathf.Max(intensity, 1 - (distToMax / threshold));
            }

            return Mathf.Clamp01(intensity);
        }

        /*
        * Clamps values by only returning them if they are within the limits.
        * @param value current value.
        * @param limits the allowed values min and max.
        * @return value if it is within limits.
        */
        bool IsClamped(float value, Vector2 limits)
        {
            return value <= limits.x || value >= limits.y;
        }
    }
}
