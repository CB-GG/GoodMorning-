from pyicloud import PyiCloudService
from getpass import getpass
from geopy.geocoders import Nominatim
import keyring

def main():
    #must have signed into / added information to keyring via pyicloud package.
    email = "your_email_here@example.com"
    password = keyring.get_password("pyicloud", email)

    
    api = PyiCloudService(email, password)
    #If user has 2FA, will allow input of code here ; should only be needed once
    if api.requires_2fa:
        print("Two-Factor Authentication required.")
        code = input("Enter the 2FA code sent to your trusted devices: ")
        result = api.validate_2fa_code(code)
        if not result:
            print("Invalid 2FA code. Exiting...")
            return
        print("2FA authentication successful.")

    if not api.devices:
        print("No devices found on this iCloud account.")
        return

    #change number here to the desired device. If unkown, first print devices to view index.
    device = device = api.devices[3]
    

    if device:
        location = device.location()
        if location:
            latitude = location['latitude']
            longitude = location['longitude']
            
            
            

            # Use geopy to find the city
            geolocator = Nominatim(user_agent="device_location_finder")
            try:
                location_info = geolocator.reverse((latitude, longitude), language='en')
                address = location_info.raw.get('address', {})
                
                
                city = (
                    address.get('city') or
                    address.get('town') or
                    address.get('village') or
                    address.get('hamlet') or
                    "Unknown City"
                )
                if city == "Unkown City":
                    #insert city to default to here
                    city = "Morgantown"
            except Exception as e:
                print(f"Error finding city: {e}")
        else:
            print(f"Location not available for {device['name']}")
    return city 
    

if __name__ == "__main__":
    main()
