# Copyright 2020 Pulser Development Team
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from dataclasses import dataclass
from typing import ClassVar
import warnings


@dataclass(init=False, repr=False, frozen=True)
class Channel:
    """Base class of a hardware channel.

    Not to be initialized itself, but rather through a child class and the
    ``Local`` or ``Global`` classmethods.

    Attributes:
        name: The name of channel.
        basis: The addressed basis name.
        addressing: "Local" or "Global".
        max_abs_detuning: Maximum possible detuning (in rad/µs), in absolute
            value.
        max_amp: Maximum pulse amplitude (in rad/µs).
        retarget_time: Maximum time to change the target (in ns).
        max_targets: How many qubits can be addressed at once by the same beam.
        clock_period: The duration of a clock cycle (in ns). The duration of a
            pulse or delay instruction is enforced to be a multiple of the
            clock cycle.
        min_duration: The shortest duration an instruction can take.
        max_duration: The longest duration an instruction can take.

    Example:
        To create a channel targeting the 'ground-rydberg' transition globally,
        call ``Rydberg.Global(...)``.
    """

    name: ClassVar[str]
    basis: ClassVar[str]
    addressing: str
    max_abs_detuning: float
    max_amp: float
    retarget_time: int = None
    max_targets: int = 1
    clock_period: int = 4       # ns
    min_duration: int = 16      # ns
    max_duration: int = 67108864        # ns

    @classmethod
    def Local(cls, max_abs_detuning, max_amp, retarget_time=220, **kwargs):
        """Initializes the channel with local addressing.

        Args:
            max_abs_detuning (float): Maximum possible detuning (in rad/µs), in
                absolute value.
            max_amp(float): Maximum pulse amplitude (in rad/µs).
            retarget_time (int): Maximum time to change the target (in ns).
        """

        return cls('Local', max_abs_detuning, max_amp,
                   retarget_time=retarget_time, **kwargs)

    @classmethod
    def Global(cls, max_abs_detuning, max_amp, **kwargs):
        """Initializes the channel with global addressing.

        Args:
            max_abs_detuning (float): Maximum possible detuning (in rad/µs), in
                absolute value.
            max_amp(float): Maximum pulse amplitude (in rad/µs).
        """

        return cls('Global', max_abs_detuning, max_amp, **kwargs)

    def validate_duration(self, duration):
        """Validates and adapts the duration of an instruction on this channel.

        Args:
            duration (int): The duration to validate.
        """
        try:
            _duration = int(duration)
        except (TypeError, ValueError):
            raise TypeError("duration needs to be castable to an int but "
                            "type %s was provided" % type(duration))

        if duration < self.min_duration:
            raise ValueError("duration has to be at least "
                             + f"{self.min_duration} ns.")

        if duration > self.max_duration:
            raise ValueError("duration can be at most "
                             + f"{self.max_duration} ns.")

        if duration % self.clock_period != 0:
            _duration += self.clock_period - _duration % self.clock_period
            warnings.warn(f"A duration of {duration} ns is not a multiple of "
                          f"the channel's clock period ({self.clock_period} "
                          f"ns). It was rounded up to {_duration} ns.")
        return _duration

    def __repr__(self):
        s = ".{}(Max Absolute Detuning: {} rad/µs, Max Amplitude: {} rad/µs"
        config = s.format(self.addressing, self.max_abs_detuning, self.max_amp)
        if self.addressing == 'Local':
            config += f", Target time: {self.retarget_time} ns"
            if self.max_targets > 1:
                config += f", Max targets: {self.max_targets}"
        config += f", Basis: '{self.basis}'"
        return self.name + config + ")"


@dataclass(init=True, repr=False, frozen=True)
class Raman(Channel):
    """Raman beam channel.

    Channel targeting the transition between the hyperfine ground states, in
    which the 'digital' basis is encoded. See base class.
    """
    name: ClassVar[str] = 'Raman'
    basis: ClassVar[str] = 'digital'


@dataclass(init=True, repr=False, frozen=True)
class Rydberg(Channel):
    """Rydberg beam channel.

    Channel targeting the transition between the ground and rydberg states,
    thus enconding the 'ground-rydberg' basis. See base class.
    """
    name: ClassVar[str] = 'Rydberg'
    basis: ClassVar[str] = 'ground-rydberg'


@dataclass(init=True, repr=False, frozen=True)
class Microwave(Channel):
    """Microwave adressing channel.

    Channel targeting the transition between two rydberg states, thus encoding
    the 'XY' basis. See base class.
    """
    name: ClassVar[str] = 'Microwave'
    basis: ClassVar[str] = 'XY'
