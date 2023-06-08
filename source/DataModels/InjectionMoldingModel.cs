using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Collections.Generic;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using Bogus;

namespace DataModels
{
    public class InjectionMoldingModel : BaseDataModel
    {
        public InjectionMoldingModel(string gatewayId, string deviceId, Dictionary<string, string> properties = null) : base(gatewayId, deviceId, properties)
        {

        }

        public override IList<string> GenerateTelemetry()
        {
            var strMessages = new List<string>();

            return strMessages;
        }
    }

}