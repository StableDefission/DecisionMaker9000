```markdown
# DecisionMaker9000

DecisionMaker9000 is a PyQt5 application designed to help users make decisions by randomly selecting options based on given weights.

## Features

- Add and weight options for decision-making.
- Save and load lists of options.
- Customize application theme (Dark or Light).
- Randomly select an option with a simple interface.

## Installation

To install the required dependencies, run the `install.bat` file. This will set up the necessary Python packages and environment settings.

```batch
./install.bat
```

## Running the Application

To start the application, execute the `run.bat` file:

```batch
./run.bat
```

## Usage

1. **Add Options:** Enter an option in the text box and specify a weight using the spin box, then click "Add" to add the option to the list.
2. **Manage Options:** Options can be saved into lists, loaded from saved lists, and deleted as needed.
3. **Settings:** Access the settings dialog through the "Settings" button to adjust the duration of the decision process and the application theme.
4. **Start Decision Making:** Click "Start" to begin the random selection process. The chosen option will be displayed prominently in the application window.

## Customization

Users can choose between a Dark and Light theme for the application through the settings dialog.

## File Structure

- `install.bat`: Batch file to install required Python libraries.
- `run.bat`: Batch file to run the application.
- `lists/`: Directory where the lists of options are saved.
- `settings.json`: Configuration file where application settings are stored.

## Dependencies

- Python 3.x
- PyQt5

Make sure you have Python installed on your computer and the PyQt5 library, which can be installed using the `install.bat` script.

## Contributing

Contributions to the DecisionMaker9000 are welcome. Please feel free to fork the repository, make your changes, and submit a pull request.

## License

Specify your license here or indicate that it is open-source.

```
