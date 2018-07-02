from api.conditioners import APICEMConditioner,APICEMErrorConditioner

class DeviceSNConditioner(APICEMConditioner):
    def condition(self,response):
        return super().condition(response) and 'serialNumber' in response.document['response']
