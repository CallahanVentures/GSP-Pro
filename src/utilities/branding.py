import emoji

ascii_logo = """
                                           .:---      ..
                                   :--:  -#*=--=#*:+##***#*:
                                :*#=-:-*##.     .+%=.     :#*
                               -%:      .                  .%#-==-
                            :=+@+                           +#+--=#*
                          +%+-:::                                  #*
                        .%+.       .::.                            *%
                        #+        .%@@#  ::      :-   :%@%-       +@+
                        #*.        =##=  -%:     *%   -%@@-        .##
                         =#%.             -#+-::=%-     .           :@-
                          %+                :=+=-.                  :@-
                         :@:                                       .#%
                          #*:.  -:                               .=%+
                           :=***@+       ..        :       :+***#*=.
                                -@+:.  .:@%-      :@#-.  .=%#%=
                               .#*=*####*+=##*==+#%==*####*=:-##
                    ::---==+++*%@#########***#%%#*++====-::::::*#
                   -@*++++=====----------========+++***#%+:::::-%=
                   .@+----------------------------------=@=:::::**
                    @*---------------===-----------------%#:::::#*
                    *%-------------=#==+#**+-------------*@-:::=@.
                    :@=----------=#*-::::::=**-----------=@#*#*#%++=-
                     ##----------**:::::::::=%------------@*%+::##-=%@
                     -@=----------+*#-:++=*#+-------------%*=#***::+@-
                      %#------------=++===----------------##:::::-#%.
                      :@+---------------------------------*%:::-#%-
                       =@=--------------------------------+@:-#%=
                        +####**++==========--------------=+@%#-
                             .:-===++++++++**************++=:

"""


application_name = "GSP Pro"
application_version = "v1.0.0"
heart_emoji = emoji.emojize(":blue_heart:")
application_credits = f"""Developed with {heart_emoji} by Callahan Ventures LLC - https://callahanventures.com/

Special thanks to:
sarperavci (https://github.com/sarperavci/GoogleRecaptchaBypass)

For providing a blueprint on solving RECAPTCHAV2"""

application_features = {
    "Automatic Data Backups",
    "Automatic Search Parsing",
    "Proxy Rotation",
    "Proxy Support (HTTP/HTTPS/SOCKS4/SOCKS5)",
    "Proxy Verification",
    "RECAPTCHAV2 Detection",
    "RECAPTCHAV2 Solving",
}


def display_company_logo():
    print(ascii_logo)
    print()


def display_application_info():
    print(application_name, application_version)
    print(application_credits)
    print()
    print("Feature List:")
    for feature in application_features:
        print(feature)
    print()


def show_branding():
    display_company_logo()
    display_application_info()
