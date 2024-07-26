class Base_Flow:
    def __init__(self,wa_id, wa_name, function_middleware,sentence):
        self.wa_id = wa_id
        self.wa_name = wa_name
        self.function_middleware = function_middleware
        self.sentence = sentence

    def get_wa_id(self):
        return self.wa_id

    def get_wa_name(self):
        return self.wa_name

    def get_function_middleware(self):
        return self.function_middleware