using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Net.Sockets;
using System.Text;

public class ControllerTracker : MonoBehaviour
{
    public Transform leftAnchor;
    public Transform rightAnchor;

    UdpClient client;
    string address = "10.138.161.31";
    int port = 5005;

    void Start()
    {
        client = new UdpClient();
    }

    void Update()
    {
        if (leftAnchor != null || rightAnchor != null)
        {
            Vector3 leftController = leftAnchor.position;
            Vector3 rightController = rightAnchor.position;

            string data = leftController.x + ", " + leftController.y + ", " + leftController.z +
            "|" + rightController.x + ", " + rightController.y + ", " + rightController.z;

            byte[] payload = Encoding.UTF8.GetBytes(data);
            client.Send(payload, payload.Length, address, port);
        }
    }
}
