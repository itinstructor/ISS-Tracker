"""
    Name: ctk_horizontal_spinbox.py
    Author: William A Loring
    Created: 12/04/2024
    Description: Custom CTkinter Horizontal Spinbox
    Claude.ai used as a code helper
"""
import customtkinter as ctk


class CTkHorizontalSpinbox(ctk.CTkFrame):
    """
    A custom spinbox-like widget for interval selection using 
    CustomTkinter components.
    """

    def __init__(self, master, min_value=1, max_value=300,
                 initial_value=10, step=1, width=200,
                 command=None, **kwargs):
        """
        Initialize the custom spinbox.

        :param master: Parent widget
        :param min_value: Minimum allowed value
        :param max_value: Maximum allowed value
        :param initial_value: Starting value
        :param step: Increment/decrement step
        :param width: Width of the widget
        :param command: Callback function when value changes
        """
        super().__init__(master, **kwargs)

        # Validation parameters
        self._min = min_value
        self._max = max_value
        self._step = step
        self._command = command

        # Configure grid layout
        self.grid_columnconfigure((0, 2), weight=0)
        self.grid_columnconfigure(1, weight=1)

        # Decrease button
        self._decrease_btn = ctk.CTkButton(
            self,
            text="-",
            width=40,
            command=self._decrease_value
        )
        self._decrease_btn.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        # Entry for displaying/editing value
        self._entry = ctk.CTkEntry(
            self,
            width=width-80,  # Adjust for buttons
            justify="center"
        )
        self._entry.grid(row=0, column=1, padx=5, sticky="ew")

        # Bind return and focus out events for validation
        self._entry.bind('<Return>', self._validate_entry)
        self._entry.bind('<FocusOut>', self._validate_entry)

        # Increase button
        self._increase_btn = ctk.CTkButton(
            self,
            text="+",
            width=40,
            command=self._increase_value
        )
        self._increase_btn.grid(row=0, column=2, padx=(5, 0), sticky="ew")

        # Set initial value
        self.set(initial_value)

    def _validate_entry(self, event=None):
        """
        Validate the entry and adjust value if needed.

        :param event: Optional event that triggered validation
        :return: 'break' to prevent default event handling
        """
        try:
            # Try to convert entry to integer
            value = int(float(self._entry.get()))

            # Clamp value between min and max
            value = max(self._min, min(self._max, value))

            # Set the validated value
            self.set(value)

            # Call the command if provided
            if self._command:
                self._command(value)

        except ValueError:
            # If conversion fails, reset to last valid value
            self.set(self._current_value)

        return 'break'

    def _increase_value(self):
        """
        Increase the current value by step.
        """
        new_value = min(self._max, self._current_value + self._step)
        self.set(new_value)

        # Call command if provided
        if self._command:
            self._command(new_value)

    def _decrease_value(self):
        """
        Decrease the current value by step.
        """
        new_value = max(self._min, self._current_value - self._step)
        self.set(new_value)

        # Call command if provided
        if self._command:
            self._command(new_value)

    def set(self, value):
        """
        Set the current value, ensuring it's within bounds.

        :param value: Value to set
        """
        # Clamp value between min and max
        self._current_value = max(self._min, min(self._max, int(value)))

        # Update entry text
        self._entry.delete(0, 'end')
        self._entry.insert(0, str(self._current_value))

    def get(self):
        """
        Get the current value.

        :return: Current value as an integer
        """
        return self._current_value
