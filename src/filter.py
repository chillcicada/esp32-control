class KalmanFilter:
    def __init__(self, initial_state, initial_uncertainty, process_variance, measurement_variance):
        self.state = initial_state
        self.uncertainty = initial_uncertainty
        self.process_variance = process_variance
        self.measurement_variance = measurement_variance

    def predict(self):
        # Predict the next state
        self.state = self.state  # In a simple model, state remains the same
        self.uncertainty += self.process_variance

    def update(self, measurement):
        # Compute Kalman Gain
        kalman_gain = self.uncertainty / (self.uncertainty + self.measurement_variance)

        # Update the state with measurement
        self.state += kalman_gain * (measurement - self.state)

        # Update the uncertainty
        self.uncertainty *= 1 - kalman_gain

    def get_state(self):
        return self.state
