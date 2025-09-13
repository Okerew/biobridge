class AutomatedLiquidHandler:
    def __init__(self, num_channels=8, max_volume=1000):
        """
        Initialize the Automated Liquid Handler.

        :param num_channels: Number of pipette channels.
        :param max_volume: Maximum volume (in microliters) that each channel can handle.
        """
        self.num_channels = num_channels
        self.max_volume = max_volume
        self.current_volume = [0] * num_channels
        self.position = (0, 0)  # (x, y) position of the pipette
        self.tips_attached = [False] * num_channels  # Track if tips are attached

    def move_to(self, x, y):
        """
        Move the pipette to the specified (x, y) position.

        :param x: X-coordinate.
        :param y: Y-coordinate.
        """
        self.position = (x, y)
        print(f"Moved to position ({x}, {y})")

    def aspirate(self, volume, channel):
        """
        Aspirate (draw in) a specified volume of liquid.

        :param volume: Volume to aspirate (in microliters).
        :param channel: Channel number to use (1-indexed).
        """
        if channel < 1 or channel > self.num_channels:
            raise ValueError("Invalid channel number")

        if volume > self.max_volume:
            raise ValueError("Volume exceeds maximum capacity")

        if not self.tips_attached[channel - 1]:
            raise ValueError(f"No tip attached to channel {channel}")

        self.current_volume[channel - 1] += volume
        print(f"Aspirated {volume} uL using channel {channel}")

    def dispense(self, volume, channel):
        """
        Dispense a specified volume of liquid.

        :param volume: Volume to dispense (in microliters).
        :param channel: Channel number to use (1-indexed).
        """
        if channel < 1 or channel > self.num_channels:
            raise ValueError("Invalid channel number")

        if volume > self.current_volume[channel - 1]:
            raise ValueError("Not enough liquid in the channel to dispense")

        if not self.tips_attached[channel - 1]:
            raise ValueError(f"No tip attached to channel {channel}")

        self.current_volume[channel - 1] -= volume
        print(f"Dispensed {volume} uL using channel {channel}")

    def change_tip(self, channel):
        """
        Change the pipette tip for a specified channel.

        :param channel: Channel number to change the tip (1-indexed).
        """
        if channel < 1 or channel > self.num_channels:
            raise ValueError("Invalid channel number")

        self.tips_attached[channel - 1] = True
        print(f"Changed tip for channel {channel}")

    def wash_tip(self, channel):
        """
        Wash the pipette tip for a specified channel.

        :param channel: Channel number to wash the tip (1-indexed).
        """
        if channel < 1 or channel > self.num_channels:
            raise ValueError("Invalid channel number")

        if not self.tips_attached[channel - 1]:
            raise ValueError(f"No tip attached to channel {channel}")

        self.current_volume[channel - 1] = 0
        print(f"Washed tip for channel {channel}")

    def get_status(self):
        """
        Get the status of the Automated Liquid Handler.

        :return: A dictionary containing the status of the handler.
        """
        status = {
            "position": self.position,
            "current_volume": self.current_volume,
            "tips_attached": self.tips_attached
        }
        return status

    def get_current_volume(self, channel):
        """
        Get the current volume of liquid in a specified channel.

        :param channel: Channel number to check (1-indexed).
        :return: Current volume in the specified channel (in microliters).
        """
        if channel < 1 or channel > self.num_channels:
            raise ValueError("Invalid channel number")

        return self.current_volume[channel - 1]
