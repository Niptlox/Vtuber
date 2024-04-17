from typing import NamedTuple, List

NO_TILT = 0
TILT_LEFT = 1
TILT_RIGHT = 2


class FaceState(NamedTuple):
    left_eye_closed: bool
    right_eye_closed: bool
    left_eye_cof: float
    right_eye_cof: float
    eyes_closed: bool
    mouth_closed: bool
    tilt: int


class Face(NamedTuple):
    image: None
    all_points: List
    contours: List
    state: FaceState
