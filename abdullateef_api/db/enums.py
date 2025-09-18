import enum


class GenderEnum(enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class CountryEnum(enum.Enum):
    NG = "NG"
    UK = "UK"
    US = "US"
    CA = "CA"


class BookingStatusEnum(enum.Enum):
    REGISTERED = "registered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    MOVED = "moved"


class PaymentTypeEnum(enum.Enum):
    REGISTRATION = "registration"
    INSTALLMENT = "installment"


class CommissionStatusEnum(enum.Enum):
    PENDING = "pending"
    PAID = "paid"
