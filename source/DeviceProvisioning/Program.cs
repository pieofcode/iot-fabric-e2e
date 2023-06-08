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
    class Program
    {
        // Azure Device Provisioning Service (DPS) Global Device Endpoint.
        private const string GlobalDeviceEndpoint = "global.azure-devices-provisioning.net";

        // Azure Device Provisioning Service (DPS) ID Scope.
        private static string dpsIdScope = "0ne002D6D43";

        // Certificate (PFX) File Name.
        private static string s_certificateFileBasePath = $"../Certs/X509/device_certs";

        // Certificate (PFX) Password. Better to use a Hardware Security Module for production devices.
        private static string s_certificatePassword = "1234";

        static void Main(string[] args)
        {
             if (args.Length != 1) 
            {
                Console.WriteLine("Missing Command Line Args: [Device Name]");
                Environment.Exit(1);
            }

            var deviceName = args[0];
            var certPath = $"{s_certificateFileBasePath}/{deviceName}-device.cert.pfx";

            // Load the device certificate
            X509Certificate2 certificate = LoadProvisioningCertificate(certPath);

            //Create a provisioning device Client
            using (var security = new SecurityProviderX509Certificate(certificate))
            {
                using (var transport = new ProvisioningTransportHandlerAmqp(TransportFallbackType.TcpOnly))
                {
                    //Create provisioning device client
                    ProvisioningDeviceClient provisioningDeviceClient = 
                        ProvisioningDeviceClient.Create(GlobalDeviceEndpoint, dpsIdScope, security, transport);
                    
                    //Run provisioning Logic
                    var provDeviceLogic = new ProvisioningDeviceLogic(provisioningDeviceClient, security);
                    provDeviceLogic.RunAsync().GetAwaiter().GetResult();
                }
            }
        }

        private static X509Certificate2 LoadProvisioningCertificate(string certPath)
        {
            var certificateCollection = new X509Certificate2Collection();
            certificateCollection.Import(certPath, s_certificatePassword, X509KeyStorageFlags.UserKeySet);

            X509Certificate2 certificate = null;

            foreach (X509Certificate2 element in certificateCollection)
            {
                Console.WriteLine($"Found certificate: {element?.Thumbprint} {element?.Subject}; PrivateKey: {element?.HasPrivateKey}");
                if (certificate == null && element.HasPrivateKey)
                {
                    certificate = element;
                }
                else
                {
                    element.Dispose();
                }
            }

            if (certificate == null)
            {
                throw new FileNotFoundException($"{certPath} did not contain any certificate with a private key.");
            }

            Console.WriteLine($"Using certificate {certificate.Thumbprint} {certificate.Subject}");
            return certificate;
        }
    }
    
}
