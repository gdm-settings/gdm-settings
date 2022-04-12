# Translation Manual

In this document, are the instructions for translating 'Login Manager Settings' app

## Prerequisites

You need the following things before starting to translate

- [Poedit](https://poedit.net)

- A copy of the source code for this app

  You can get a [tar.gz](https://github.com/realmazharhussain/gdm-settings/archive/refs/heads/main.tar.gz) archive and extract it **OR** you can run the following command in terminal to get it

  ```bash
  git clone --depth=1 https://github.com/realmazharhussain/gdm-settings.git
  ```

## How to translate?

### Create a new translation

1. Open main folder of source code inside a terminal

2. Add your language code (on its own line) to `LINGUAS` file in `po` sub-folder of the source code

   **Language Code examples:** `en` for 'English', `en_US` for 'English (United States)', `ur` for 'Urdu', `ur_PK` for 'Urdu (Pakistan)', `ar` for 'Arabic', etc.

   **Note:** It is recommended (but not necessary) that you keep language codes in `LINGUAS` file alphabetically sorted

3. Run the following command

   ```bash
   ./po/update-pot-file.sh
   ```

   This will create a file named `gdm-settings.pot`

4. Open Poedit

5. Click on 'Create new...' and choose newly created `gdm-settings.pot` file

6. Select your language

7. In the top menu-bar, Click on 'Edit' and then on 'Preferences' in the menu that appears

8. Fill in your name and email address and then close the preferences window

9. Start translating

   **Note:** Text `translator-credits` is special. Don't translate it. You can put your information here in place of translated text (in your language) and it will show up in the about dialog of this application. It is recommended that you put text here with following format (including '<' and '>')

   `name <email>`

10. Press 'Ctrl+S' or click on 'Save' button to save your translations

Now, you have successfully created translation for a new language.

### Update existing translation

1. Open main folder of source code inside a terminal

2. Run the following command

   ```bash
   ./po/update-pot-file.sh
   ```

   This will create a file named `gdm-settings.pot`

3. Open Poedit

4. Click on 'Browse files' and choose `.po` file for your language

   For example, `ur.po` for Urdu, `ur_PK.po` for Urdu (Pakistan), `en_US.po` for English (United States), etc.

   **Note:** `.po` files are located in `po` sub-folder of the source code

5. In the top menu-bar, Click on 'Translation' and then on 'Update from POT file...' in the menu that appears

6. Click on 'OK'

7. In the top menu-bar, Click on 'Edit' and then on 'Preferences' in the menu that appears

8. Fill in your name and email address and then close the preferences window

9. Start translating

   **Note:** Text `translator-credits` is special. Don't translate it. You can put your information here in place of translated text (in your language) and it will show up in the about dialog of this application. It is recommended that you put text here with following format (including '<' and '>')

   `name <email>`

10. Press 'Ctrl+S' or click on 'Save' button to save your translations
   
### Submit your translation

Create a pull request

**OR**

[Open an issue](https://github.com/realmazharhussain/gdm-settings/issues/new?assignees=&labels=translation&template=translation_submission.yml&title=%5BL10N%5D+) and provide your translation file there

## Get notified when translations need updates

You can subscribe to the '[Translation Updates](https://github.com/realmazharhussain/gdm-settings/discussions/23)' discussion and get notified when there's a new release coming and requires translations to be updated for new/modified text.
