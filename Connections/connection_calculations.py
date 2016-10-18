import math

class ConnectionCalculations(object):
    """Perform common calculations for connection components in abstract class.

    Note:
        This is the parent class for each connection module's calculation class.
    """

    def bolt_shear(self, bolt_diameter, number_of_bolts, bolt_fu):
        """Calculate factored shear capacity of bolt(s) based on IS 800, Cl 10.3.3.

        Args:
            bolt_diameter (int)
            number_of_bolts (int)
            bolt_fu (int)

        Returns:
            Factored shear capacity of bolt(s) as float.

        Note:
            Bolt factored shear capacity = bolt_fu * number_of_bolts * Area_bolt_net_tensile / (square_root(3) * gamma_mb)
            Assumptions:
            1)for all bolts, shear plane passes through threaded area
            2)for all bolts, tensile stress area equals the threaded area
            3)reduction factors for long joints, large grip lengths, packing plates are not applicable
            4) values for tensile stress area (mm^2) are taken from Table 5.9 in DoSS - N. Subramanian

        """
        gamma_mb = 1.25
        bolt_area = {
            '12': 84.3,
            '16': 157,
            '20': 245,
            '22': 303,
            '24': 353,
            '27': 459,
            '30': 561,
            '36': 817
        }[str(bolt_diameter)]
        bolt_nominal_shear_capacity = bolt_fu * number_of_bolts * bolt_area / math.sqrt(3) / 1000
        return round(bolt_nominal_shear_capacity / gamma_mb, 3)

    def bolt_bearing(self, bolt_diameter, number_of_bolts, thickness_plate, k_b, plate_fu):
        """Calculate factored bearing capacity of bolt(s) based on IS 800, Cl 10.3.4.

        Args:
            bolt_diameter (int)
            number_of_bolts (int)
            thickness_plate (float)
            k_b (float)
            plate_fu (int)

        Return:
             Factored bearing capacity of bolt(s) as float.

        Note:
            Bolt factored bearing capacity = 2.5 * k_b * bolt_diameter * sum_thickness_of_connecting_plates * f_u / gamma_mb
            #TODO : implement reduction factor 0.7 for over size holes - Cl 10.3.4

        """
        gamma_mb = 1.25
        bolt_nominal_bearing_capacity = 2.5 * k_b * bolt_diameter * number_of_bolts * thickness_plate * plate_fu / (
        1000)
        return round(bolt_nominal_bearing_capacity / gamma_mb, 3)

    def bolt_hole_clearance(self, bolt_hole_type, bolt_diameter, custom_hole_clearance):
        """Calculate bolt hole clearance.

        Args:
            bolt_diameter (int)

        Returns:
            hole_clearance (int)

        Note:
            Reference:
            IS 800, Table 19 (Cl 10.2.1) : Clearances for Fastener Holes

        """
        if bolt_hole_type == 1:  # standard hole
            hole_clearance = {
                12: 1,
                14: 1,
                16: 2,
                18: 2,
                20: 2,
                22: 2,
                24: 2,
                30: 3,
                36: 3
            }[bolt_diameter]
        elif bolt_hole_type == 0:  # over size hole
            hole_clearance = {
                12: 3,
                14: 3,
                16: 4,
                18: 4,
                20: 4,
                22: 4,
                24: 6,
                30: 8,
                36: 8
            }[bolt_diameter]
        if custom_hole_clearance is not None:
            hole_clearance = custom_hole_clearance  # units: mm
        return hole_clearance  # units: mm

    def calculate_distances(self, bolt_diameter, bolt_hole_diameter, min_edge_multiplier):
        """Calculate minimum pitch, gauge, end and edge distances.

        Args:
            bolt_diameter (int)
            bolt_hole_diameter (int)
            min_edge_multiplier (float)

        Returns:
            None

        Note:
            # Minimum pitch and gauge IS 800 Cl 10.2.2
            # Min edge and end distances IS 800 Cl 10.2.4.2
        """
        # Minimum pitch and gauge IS 800 Cl 10.2.2
        self.min_pitch = int(2.5 * bolt_diameter)
        self.min_gauge = int(2.5 * bolt_diameter)

        # Min edge and end distances IS 800 Cl 10.2.4.2
        self.min_end_dist = int(math.ceil(min_edge_multiplier * bolt_hole_diameter))
        self.min_edge_dist = int(math.ceil(min_edge_multiplier * bolt_hole_diameter))

        # TODO: rethink rounding off of MINIMUM distances
        # round off the actual distances and check against minimum
        if self.min_pitch % 5 != 0 or self.min_gauge % 5 != 0:
            self.min_pitch = ((self.min_pitch / 5) + 1) * 5 - self.min_pitch % 5
            self.min_gauge = ((self.min_pitch / 5) + 1) * 5 - self.min_pitch % 5
        if self.min_edge_dist % 5 != 0 or self.min_end_dist % 5 != 0:
            self.min_edge_dist = int((int(self.min_edge_dist / 5) + 1) * 5)
            self.min_end_dist = int((int(self.min_end_dist / 5) + 1) * 5)

        # Max spacing IS 800 Cl 10.2.3.1
        self.max_spacing = math.ceil(min(32 * thickness_governing, 300))
        # print "Max spacing = " + str(self.max_spacing)

        # Max spacing IS 800 Cl 10.2.4.3
        self.max_edge_dist = math.ceil((12 * thickness_governing * math.sqrt(250 / self.angle_fy)).real)
        # print "Max edge distance = " + str(self.max_edge_dist)

        # Cl 10.2.4.3 in case of corrosive influences, the maximum edge distance shall not exceed
        # 40mm plus 4t, where t is the thickness of the thinner connected plate.
        # self.max_edge_dist = min(self.max_edge_dist, 40 + 4*thickness_governing)

    def calculate_kb(self):
        """Calculate k_b for bearing capacity of bolt

        Args:
            None

        Returns:
            None

        """
        self.k_b = min(self.end_dist / float(3 * self.bolt_hole_diameter),
                       self.pitch / float(3 * self.bolt_hole_diameter) - 0.25,
                       self.bolt_fu / float(self.angle_fu),
                       1)
        self.k_b = round(self.k_b, 3)
