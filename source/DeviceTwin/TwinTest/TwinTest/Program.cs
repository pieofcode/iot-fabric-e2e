using Microsoft.Azure.Devices;
using Microsoft.Azure.Devices.Client;
using Microsoft.Azure.Devices.Shared;
using Newtonsoft.Json;
using System;
using System.Threading.Tasks;


namespace TwinTest
{
    class Program
    {

        static string s_DeviceConnectionString = "HostName=iothub-standard-poc.azure-devices.net;SharedAccessKeyName=iothubowner;SharedAccessKey=AsdRDCcIvMDgFMFOYZL5RsvPnMFdiGUwATWNXLVyS1o=";
        static string s_Deviceid = "edge-dev-02";
        private static ModuleClient Client = null;
        static void ConnectionStatusChangeHandler(ConnectionStatus status,
                                                  ConnectionStatusChangeReason reason)
        {
            Console.WriteLine("Connection Status Changed to {0}; the reason is {1}",
                status, reason);
        }


        static void Main(string[] args)
        {

            var transport = Microsoft.Azure.Devices.Client.TransportType.Amqp;

            try
            {
                var twin = ReadTwinPropertiesAsync(s_Deviceid).Result;
                Console.WriteLine(twin.ToJson());

                var result = UpdateTwinPropertiesAsync(s_Deviceid, twin.ETag).Result;
            }
            catch (AggregateException ex)
            {
                Console.WriteLine("Error in sample: {0}", ex);
            }

           
        }

        static async Task<Twin> ReadTwinPropertiesAsync(string deviceId)
        {
            Console.WriteLine("Hello World!");
            var registryManager = RegistryManager.CreateFromConnectionString(s_DeviceConnectionString);
            var twin = await registryManager.GetTwinAsync(deviceId);

            return twin;
        }

        static async Task<int> UpdateTwinPropertiesAsync(string deviceId, string eTag)
        {
           
            var registryManager = RegistryManager.CreateFromConnectionString(s_DeviceConnectionString);
            var twin = await registryManager.GetTwinAsync(deviceId);
            Console.WriteLine("Sending app start time as reported property");
            TwinCollection reportedProperties = new TwinCollection();
            reportedProperties["DateTimeLastAppLaunch"] = DateTime.Now;
            // This is the piece of the twin tags we want to update
            var patch = @"{
                            tags: {
                                info: {  
                                    origin: 'Argentina',  
                                    version: '14.01'  
                                }  
                            }  
                        }";

            await registryManager.UpdateTwinAsync(deviceId, patch, eTag);

            return 0;
        }


    }
}
