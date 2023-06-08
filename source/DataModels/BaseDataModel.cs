using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Collections.Generic;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;

namespace DataModels
{
    public abstract class BaseDataModel
    {
        public string GatewayId { get; internal set; }

        public string DeviceId { get; internal set; }

        public Dictionary<string, string> Properties { get; set; }

        public int MessageCount { get; internal set; }

        public BaseDataModel(string gatewayId, string deviceId, Dictionary<string, string> properties)
        {
            // calling the set accessor of the Id property.
            Properties = properties;
            GatewayId = gatewayId;
            DeviceId = deviceId;
        }

        public abstract IList<string> GenerateTelemetry();

    }
}