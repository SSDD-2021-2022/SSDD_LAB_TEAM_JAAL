module Service {
    
    exception UnknownService { string serviceId; };
    exception TemporaryUnavailable {};

    interface Discovery {
        void announce(string serviceId, Object* service);
    };

    interface PrinterService {
        void say(string message);
    };

    interface CounterService {
        void tick();
        int getCount();
        void reset();
    };

    interface Main {
        PrinterService* getPrinterService();
        CounterService* getCounterService();
    };

};