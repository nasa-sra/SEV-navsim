import pygame
import math

class StanleyController:

    def __init__(self, k_gain=0.5):
        self.k_gain = k_gain

    def closest_point_on_segment(self, SEVpos, wp1_vec, wp2_vec):

        AB = wp2_vec - wp1_vec
        AS = SEVpos - wp1_vec

        AB_len_sq = AB.length_squared()
        if AB_len_sq == 0:
            return wp1_vec

        t = AS.dot(AB) / AB_len_sq
        t = max(0, min(1, t))  # clamp to segment

        return wp1_vec + t * AB

    def compute_cte(self, SEVpos, wp1_vec, wp2_vec):

        AB = wp2_vec - wp1_vec
        AS = SEVpos - wp1_vec

        # perpendicular distance with sign
        cross = AB.x * AS.y - AB.y * AS.x
        cte = cross / AB.length() if AB.length() > 0 else 0

        return cte

    def heading_error(self, SEV_heading, wp1_vec, wp2_vec):

        path_dir = (wp2_vec - wp1_vec).normalize()
        path_angle = math.degrees(math.atan2(path_dir.y, path_dir.x))

        # smallest signed angle difference
        err = (path_angle - SEV_heading + 180) % 360 - 180
        return err

    def steering(self, SEVpos, SEV_heading, SEV_velocity, wp1, wp2):

        a = pygame.Vector2(wp1.getX(), wp1.getY())
        b = pygame.Vector2(wp2.getX(), wp2.getY())
        p = pygame.Vector2(SEVpos.x, SEVpos.y)

        # Compute errors
        cte = self.compute_cte(p, a, b)
        theta_err = self.heading_error(SEV_heading, a, b)

        # Avoid division by zero
        v = max(SEV_velocity, 0.01)

        steering_angle = theta_err + math.degrees(math.atan(self.k_gain * cte / v))

        return steering_angle