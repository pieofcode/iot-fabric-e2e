using System;
using System.Text;
using System.Threading.Tasks;
using System.IO;
using System.Text.Json;
using System.Security.Cryptography.X509Certificates;
using Microsoft.Azure.Devices.Client;
using Microsoft.Azure.Devices.Provisioning.Client;
using Microsoft.Azure.Devices.Provisioning.Client.Transport;
using Microsoft.Azure.Devices.Shared;

namespace DeviceProvisioning
{
    public class ProvisioningDeviceLogic
    {
        readonly ProvisioningDeviceClient _provClient;
        readonly SecurityProvider _security;
        DeviceClient s_deviceClient;

        // Global constants.
        const float ambientTemperature = 70;                    // Ambient temperature of a southern cave, in degrees F.
        const double ambientHumidity = 99;                      // Ambient humidity in relative percentage of air saturation.
        const double desiredTempLimit = 5;                      // Acceptable range above or below the desired temp, in degrees F.
        const double desiredHumidityLimit = 10;                 // Acceptable range above or below the desired humidity, in percentages.
        const int intervalInMilliseconds = 5000;                // Interval at which telemetry is sent to the cloud.
        enum stateEnum
        {
            off,
            on,
            failed
        }

        public ProvisioningDeviceLogic(ProvisioningDeviceClient provisioningDeviceClient, SecurityProvider security)
        {
            _provClient = provisioningDeviceClient;
            _security = security;
        }

        private static void colorMessage(string text, ConsoleColor clr)
        {
            Console.ForegroundColor = clr;
            Console.WriteLine(text);
            Console.ResetColor();
        }
        private static void greenMessage(string text)
        {
            colorMessage(text, ConsoleColor.Green);
        }

        private static void redMessage(string text)
        {
            colorMessage(text, ConsoleColor.Red);
        }

        private static void whiteMessage(string text)
        {
            colorMessage(text, ConsoleColor.White);
        }

        public async Task RunAsync()
        {
            colorMessage($"\nRegistrationID = {_security.GetRegistrationID()}", ConsoleColor.Yellow);
        }


    }
}