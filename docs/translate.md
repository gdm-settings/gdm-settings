# Translation Manual

In this document, are the instructions for translating 'Login Manager Settings' app

## Prerequisites

You need the following things before starting to translate

- A copy of the source code for this app

  You can get a [tar.gz](https://github.com/realmazharhussain/gdm-settings/archive/refs/heads/main.tar.gz) archive and extract it **OR** you can run the following command in terminal to get it

  ```bash
  git clone --depth=1 https://github.com/realmazharhussain/gdm-settings.git
  ```

- [intltool](https://launchpad.net/intltool)

- [GTranslator](https://gitlab.gnome.org/GNOME/gtranslator.git)

## How to translate?

### Configure/Prepare GTranslator

Once installed, GTranslator is available as 'Translation Editor' in the applications menu. The first time you open up GTranslator, It will present a window asking for some information (name, email, language). Fill in the information as appropriate.

If you mistyped some information and want to change it later,

1. Click on the hamburger menu (three bars) at top of the application window
2. Click on 'preferences'
3. Go to 'profiles' tab
4. Select the active profile
5. Click on 'Edit Profile'
6. Change required information
7. Click 'OK'

### Create a new translation

0. Make sure you have configured GTranslator as mentioned above

1. Open 'po' sub-folder of source code inside a terminal

2. Run the following command

   ```bash
   intltool-update --pot
   ```

   This will create a file named `untitled.pot`

3. Rename `untitled.pot` to `<your_language_code>.po`

   For example, `en.po` for 'English', `en_US.po` for 'English (United States)', `ur.po` for 'Urdu', `ur_PK` for 'Urdu (Pakistan)', `ar.po` for 'Arabic', etc.

   ```bash
   mv untitled.pot <your_language_code>.po
   ```

   **Note:** We changed file extension from `pot` to `po`

4. Add your language code (on its own line) to `LINGUAS` file

   It is recommended (but not necessary) that you keep language codes in `LINGUAS` file alphabetically sorted

5. Open GTranslator

6. Click on 'Open' and choose newly created `po` file for your language

7. Once your file is open, click on the hamburger menu (three bars) at top of the application window

8. Click on 'Edit header'

9. Fill in the information as appropriate

10. Press 'Ctrl+S' or click on 'Save' button

Now, you have successfully created translation for a new language. It does not contain any translated text yet. We will add it later in the next step.

### Update existing translation

0. Make sure you have configured GTranslator as mentioned above

1. Open 'po' sub-folder of source code inside a terminal

2. Run the following command

   ```bash
   intltool-update <your_language_code>
   ```

   This will add/remove text from translation file for your language (`<your_language_code>.po`) based on what text has been added/removed from the application itself

3. Open GTranslator

4. Click on 'Open' and choose translation file for your language (`<your_language_code>.po`)

5. Change/add translations

   Click on any text and you can change its translation by changing text in 'Translated Text' text box

   **Note:** Do not change anything in 'Original Message' text box. Otherwise, translation will be rendered useless.
   
   **Also Note:** Text `translator-credits` is special. Don't translate it. You can put your information here in place of translated text (in your language) and it will show up in the about dialog of this application. It is recommended that you put text here with following format
   
   `name <email>`

6. Save your translations by pressing 'Ctrl+S' or clicking on 'Save'

### Submit your translation

Create a pull request

**OR**

[Open an issue](https://github.com/realmazharhussain/gdm-settings/issues/new?assignees=&labels=translation&template=translation_submission.yml&title=%5BL10N%5D+) and provide your translation file there
