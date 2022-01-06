
class ApplicationException(Exception):
    msg = "Application Exception occured"

class FileVerificationFailedExcpetion(ApplicationException):
    msg = "File Verification Failed. Check for any field is missing, or file is empty"

class PositionAlreadyUploaded(ApplicationException):
    msg = "Position file already uploaded for thsi date. Check the date on the file"

class FileUploadFailed(ApplicationException):
    msg = "File upload failed. Let your system administrator know by emailing about this message"

class FileFormatException(ApplicationException):
    msg = "This action expects the file in a specific format. This file did not meet that criteria"

class FileNotChosenException(ApplicationException):
    msg = "You may not have chosen a file to upload. Choose a file to upload"

class UserRegistrationFailedException(ApplicationException):
    msg = "User registration Failed"

class PositionsSaveException(ApplicationException):
    msg = "Positions could not be saved"

class DataFetchException(ApplicationException):
    def __init__(self, function_name, reason):
        self.msg = f"Data could not be fetched from the underlying source, {function_name} {reason}"