class KalmanFilter:
    """A Simple 1D Kalman Filter Implementation."""

    def __init__(self, initial_state, initial_uncertainty, process_variance, measurement_variance):
        """Initialize the Kalman Filter with given parameters."""
        self.state = initial_state
        self.uncertainty = initial_uncertainty
        self.process_variance = process_variance
        self.measurement_variance = measurement_variance

    def predict(self):
        """Predict the next state."""
        self.uncertainty += self.process_variance

    def update(self, measurement):
        """Update the state with a new measurement."""
        # Compute Kalman Gain
        kalman_gain = self.uncertainty / (self.uncertainty + self.measurement_variance)

        # Update the state with measurement
        self.state += kalman_gain * (measurement - self.state)

        # Update the uncertainty
        self.uncertainty *= 1 - kalman_gain

        return self.state


if __name__ == '__main__':
    pass
