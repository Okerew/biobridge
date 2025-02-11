from setuptools import Extension
import pybind11
from hatchling.builders.hooks.plugin.interface import BuildHookInterface

class BuildExtHook(BuildHookInterface):
    def initialize(self, version, build_data):  
        self.extensions = [
            Extension(
                "biobridge.visualizer",
                ["biobridge/cpp/visualizer.cpp"],
                include_dirs=[
                    pybind11.get_include(),
                    "/opt/homebrew/Cellar/sfml/2.6.1/include",
                ],
                library_dirs=["/opt/homebrew/Cellar/sfml/2.6.1/lib"],
                libraries=["sfml-graphics", "sfml-window", "sfml-system"],
                language="c++",
                extra_compile_args=["-std=c++11"],
            ),
            Extension(
                "biobridge.neural_network",
                ["biobridge/cpp/neural_network.cpp"],
                include_dirs=[
                    pybind11.get_include(),
                    "/opt/homebrew/Cellar/nlohmann-json/3.11.3/include",
                ],
                library_dirs=["/opt/homebrew/Cellar/nlohmann-json/3.11.3/lib"],
                language="c++",
                extra_compile_args=["-std=c++11"],
            ),
            Extension(
                name="biobridge.operations_simulator",
                sources=["biobridge/cpp/operations_simulator.cpp"],
                include_dirs=[
                    pybind11.get_include(),
                    "/opt/homebrew/Cellar/sfml/2.6.1/include",
                ],
                library_dirs=["/opt/homebrew/Cellar/sfml/2.6.1/lib"],
                libraries=["sfml-graphics", "sfml-window", "sfml-system"],
                language="c++",
                extra_compile_args=["-std=c++11"],
            ),
            Extension(
                name="biobridge.metabolic_network",
                sources=["biobridge/cpp/metabolic_network.cpp"],
                include_dirs=[
                    pybind11.get_include(),
                    "/opt/homebrew/Cellar/nlohmann-json/3.11.3/include",
                    "/opt/homebrew/Cellar/boost/1.86.0/include",
                ],
                library_dirs=[
                    "/opt/homebrew/Cellar/nlohmann-json/3.11.3/lib",
                    "/opt/homebrew/Cellar/boost/1.86.0/lib",
                ],
                libraries=["boost_filesystem", "boost_system"],
                language="c++",
                extra_compile_args=["-std=c++11"],
            ),
            Extension(
                name="biobridge.signaling_network",
                sources=["biobridge/cpp/signaling_network.cpp"],
                include_dirs=[
                    pybind11.get_include(),
                    "/opt/homebrew/Cellar/nlohmann-json/3.11.3/include",
                ],
                library_dirs=["/opt/homebrew/Cellar/nlohmann-json/3.11.3/lib"],
                libraries=["boost_filesystem", "boost_system"],
                language="c++",
                extra_compile_args=["-std=c++11"],
            ),
            Extension(
                name="biobridge.individuals",
                sources=[
                    "biobridge/cpp/consciousness_simulator.cpp",
                    "biobridge/cpp/society_simulator.cpp",
                ],
                include_dirs=[pybind11.get_include()],
                language="c++",
                extra_compile_args=["-std=c++11"],
            ),
            Extension(
                name="biobridge.immune_system",
                sources=["biobridge/cpp/immune_system.cpp"],
                include_dirs=[
                    pybind11.get_include(),
                    "/opt/homebrew/Cellar/sfml/2.6.1/include",
                ],
                library_dirs=["/opt/homebrew/Cellar/sfml/2.6.1/lib"],
                libraries=["sfml-graphics", "sfml-window", "sfml-system"],
                language="c++",
                extra_compile_args=["-std=c++11"],
            ),
            Extension(
                name="biobridge.embryo_simulator",
                sources=["biobridge/cpp/embryo_simulator.cpp"],
                include_dirs=[
                    pybind11.get_include(),
                    "/opt/homebrew/Cellar/sfml/2.6.1/include",
                ],
                library_dirs=["/opt/homebrew/Cellar/sfml/2.6.1/lib"],
                libraries=["sfml-graphics", "sfml-window", "sfml-system"],
                language="c++",
                extra_compile_args=["-std=c++11"],
            ),
            Extension(
                name="biobridge.infection_simulator",
                sources=["biobridge/cpp/infection_simulator.cpp"],
                include_dirs=[
                    pybind11.get_include(),
                    "/opt/homebrew/Cellar/sfml/2.6.1/include",
                ],
                library_dirs=["/opt/homebrew/Cellar/sfml/2.6.1/lib"],
                libraries=["sfml-graphics", "sfml-window", "sfml-system"],
                language="c++",
                extra_compile_args=["-std=c++11"],
            ),
        ]

    def get_build_data(self):
        return {
            "extensions": self.extensions,
            "pure": False, 
        }