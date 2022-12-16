class ErrorCode:
    def __init__(self, type_id, origin, field, description):
        self.type_id = type_id
        self.field = field
        self.origin = origin
        self.description = description


ERROR_1_UUID_NOT_BINARY = ErrorCode(1, "plate", "uuid", "Uuid is not binary")
ERROR_2_UUID_NOT_RIGHT_FORMAT = ErrorCode(1, "plate", "uuid", "Uuid has wrong format")
