"""
Copyright 2015 Alexandre Poirier

This file is part of Pyo Synth, a GUI written in python that helps
with live manipulation of synthesizer scripts written with the pyo library.

Pyo Synth is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published
by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

Pyo Synth is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Pyo Synth.  If not, see <http://www.gnu.org/licenses/>.
"""

from wx.lib.embeddedimage import PyEmbeddedImage

txt_ctrl_left_side = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAAwAAAAWCAYAAAD0OH0aAAAAGXRFWHRTb2Z0d2FyZQBBZG9i"
    "ZSBJbWFnZVJlYWR5ccllPAAAA2ZpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tl"
    "dCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1l"
    "dGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUu"
    "MC1jMDYwIDYxLjEzNDc3NywgMjAxMC8wMi8xMi0xNzozMjowMCAgICAgICAgIj4gPHJkZjpS"
    "REYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgt"
    "bnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wTU09Imh0dHA6"
    "Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9tbS8iIHhtbG5zOnN0UmVmPSJodHRwOi8vbnMuYWRv"
    "YmUuY29tL3hhcC8xLjAvc1R5cGUvUmVzb3VyY2VSZWYjIiB4bWxuczp4bXA9Imh0dHA6Ly9u"
    "cy5hZG9iZS5jb20veGFwLzEuMC8iIHhtcE1NOk9yaWdpbmFsRG9jdW1lbnRJRD0ieG1wLmRp"
    "ZDpGNzdGMTE3NDA3MjA2ODExOTQ1N0NGRjE3REYyQjQ3NyIgeG1wTU06RG9jdW1lbnRJRD0i"
    "eG1wLmRpZDpEMjVBMERCRUUyRkMxMUUzQTVCQThFOUMwQkE3MDBFRiIgeG1wTU06SW5zdGFu"
    "Y2VJRD0ieG1wLmlpZDpEMjVBMERCREUyRkMxMUUzQTVCQThFOUMwQkE3MDBFRiIgeG1wOkNy"
    "ZWF0b3JUb29sPSJBZG9iZSBQaG90b3Nob3AgQ1M1IE1hY2ludG9zaCI+IDx4bXBNTTpEZXJp"
    "dmVkRnJvbSBzdFJlZjppbnN0YW5jZUlEPSJ4bXAuaWlkOjA1ODAxMTc0MDcyMDY4MTE5MTA5"
    "OTM3OTYzRDA5OThGIiBzdFJlZjpkb2N1bWVudElEPSJ4bXAuZGlkOkY3N0YxMTc0MDcyMDY4"
    "MTE5NDU3Q0ZGMTdERjJCNDc3Ii8+IDwvcmRmOkRlc2NyaXB0aW9uPiA8L3JkZjpSREY+IDwv"
    "eDp4bXBtZXRhPiA8P3hwYWNrZXQgZW5kPSJyIj8+J3czdAAAAehJREFUeNpi+P//PwOx+OrV"
    "qyosDHjAtWvXDIFUGBA7ALHQ/QcPGVhwKLQGUpGXr15z3bBpC8PR4ycZPnz4yMDACEQgq9AU"
    "J3769LmirauX4cDhIwyMjEwMTExMDIxMzEA2I6oGoOLI12/eNmTlFzE8ffaCgYmZhYGJhRWo"
    "gRnIZgZrhmsAKpb6/v37/rTcQoZ79x8xMAMVMrOygWmwRqAmoA4UP0QvXLaK4cHDJwwsbOwM"
    "LKzsEA3MrEDnMIFNB/mBBWo6/6fPX1I2bNkOVARRCNIAMxnkdpDpIACzwevA4WMMP3//BSoE"
    "OYMNohjqbmQA06B598EjhEIWqMkMjBhBDtMg/u7DJ4gHQQrRnIFNA0gF0IMsSB5kxBr7MAc+"
    "ExcVA4c5I1QTAw4bYBpO62qrQz3KAnUSE8QHaJpgGg4Z62kxcPPwAP0B8zQTxHkwTVCNYA1a"
    "Wlofebi55gT7uAAVs0GSAyskxBiZoZpB6QiIkQN5lp+rHYOasgIk4oCxzczGAaFhSQTkR7TE"
    "FwQM3vaOmUsZHj1/zQDMNQz//v1l+P/vHxiDXYcleUf++PmrYf7aHQxHzl0DiwHzG1gzVg1I"
    "OS3y4bOX/kfPX2c4d/0uw6t3H3FrQNKoCaT8gdgJiOUJasAGAAIMAOsLxcOo3cDmAAAAAElF"
    "TkSuQmCC")

txt_ctrl_middle = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAAWCAYAAAABxvaqAAAAGXRFWHRTb2Z0d2FyZQBBZG9i"
    "ZSBJbWFnZVJlYWR5ccllPAAAA2ZpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tl"
    "dCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1l"
    "dGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUu"
    "MC1jMDYwIDYxLjEzNDc3NywgMjAxMC8wMi8xMi0xNzozMjowMCAgICAgICAgIj4gPHJkZjpS"
    "REYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgt"
    "bnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wTU09Imh0dHA6"
    "Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9tbS8iIHhtbG5zOnN0UmVmPSJodHRwOi8vbnMuYWRv"
    "YmUuY29tL3hhcC8xLjAvc1R5cGUvUmVzb3VyY2VSZWYjIiB4bWxuczp4bXA9Imh0dHA6Ly9u"
    "cy5hZG9iZS5jb20veGFwLzEuMC8iIHhtcE1NOk9yaWdpbmFsRG9jdW1lbnRJRD0ieG1wLmRp"
    "ZDpGNzdGMTE3NDA3MjA2ODExOTQ1N0NGRjE3REYyQjQ3NyIgeG1wTU06RG9jdW1lbnRJRD0i"
    "eG1wLmRpZDpGMzE3MjczQkUyRkMxMUUzQTVCQThFOUMwQkE3MDBFRiIgeG1wTU06SW5zdGFu"
    "Y2VJRD0ieG1wLmlpZDpGMzE3MjczQUUyRkMxMUUzQTVCQThFOUMwQkE3MDBFRiIgeG1wOkNy"
    "ZWF0b3JUb29sPSJBZG9iZSBQaG90b3Nob3AgQ1M1IE1hY2ludG9zaCI+IDx4bXBNTTpEZXJp"
    "dmVkRnJvbSBzdFJlZjppbnN0YW5jZUlEPSJ4bXAuaWlkOjA1ODAxMTc0MDcyMDY4MTE5MTA5"
    "OTM3OTYzRDA5OThGIiBzdFJlZjpkb2N1bWVudElEPSJ4bXAuZGlkOkY3N0YxMTc0MDcyMDY4"
    "MTE5NDU3Q0ZGMTdERjJCNDc3Ii8+IDwvcmRmOkRlc2NyaXB0aW9uPiA8L3JkZjpSREY+IDwv"
    "eDp4bXBtZXRhPiA8P3hwYWNrZXQgZW5kPSJyIj8+z4RL1gAAAFBJREFUeNqEjbsRgDAMQ2Vh"
    "h4RfRcUK7M42ucMsY3wsgIpX6UnovZ+8/bmw7YfTagNLW0AbJ5CDgiICIvODr0e1dGu6ZV5B"
    "zT3khyMi8AowAB+wDh1g7AaxAAAAAElFTkSuQmCC")

txt_ctrl_right_side = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAA0AAAAWCAYAAAAb+hYkAAAAGXRFWHRTb2Z0d2FyZQBBZG9i"
    "ZSBJbWFnZVJlYWR5ccllPAAAA2ZpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tl"
    "dCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1l"
    "dGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUu"
    "MC1jMDYwIDYxLjEzNDc3NywgMjAxMC8wMi8xMi0xNzozMjowMCAgICAgICAgIj4gPHJkZjpS"
    "REYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgt"
    "bnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wTU09Imh0dHA6"
    "Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9tbS8iIHhtbG5zOnN0UmVmPSJodHRwOi8vbnMuYWRv"
    "YmUuY29tL3hhcC8xLjAvc1R5cGUvUmVzb3VyY2VSZWYjIiB4bWxuczp4bXA9Imh0dHA6Ly9u"
    "cy5hZG9iZS5jb20veGFwLzEuMC8iIHhtcE1NOk9yaWdpbmFsRG9jdW1lbnRJRD0ieG1wLmRp"
    "ZDpGNzdGMTE3NDA3MjA2ODExOTQ1N0NGRjE3REYyQjQ3NyIgeG1wTU06RG9jdW1lbnRJRD0i"
    "eG1wLmRpZDpGMzE3MjczN0UyRkMxMUUzQTVCQThFOUMwQkE3MDBFRiIgeG1wTU06SW5zdGFu"
    "Y2VJRD0ieG1wLmlpZDpGMzE3MjczNkUyRkMxMUUzQTVCQThFOUMwQkE3MDBFRiIgeG1wOkNy"
    "ZWF0b3JUb29sPSJBZG9iZSBQaG90b3Nob3AgQ1M1IE1hY2ludG9zaCI+IDx4bXBNTTpEZXJp"
    "dmVkRnJvbSBzdFJlZjppbnN0YW5jZUlEPSJ4bXAuaWlkOjA1ODAxMTc0MDcyMDY4MTE5MTA5"
    "OTM3OTYzRDA5OThGIiBzdFJlZjpkb2N1bWVudElEPSJ4bXAuZGlkOkY3N0YxMTc0MDcyMDY4"
    "MTE5NDU3Q0ZGMTdERjJCNDc3Ii8+IDwvcmRmOkRlc2NyaXB0aW9uPiA8L3JkZjpSREY+IDwv"
    "eDp4bXBtZXRhPiA8P3hwYWNrZXQgZW5kPSJyIj8+Gk2Y5wAAAh5JREFUeNqUlM9rE1EQx7/v"
    "Z9akCk2aFlNrKQ1SE6yIglhqpUUPUlrQU2uhB+/ePXjxb+ilFMVbC0UE8SL0aqWI10Q3Vosi"
    "QqUWvXkwWWdedjdZ0oAuDLPvvfnMzM7MW1GpVMoADkql0j7+8dHv/dqzXC6LarXK6z2SlySb"
    "5ORbN0ic6Cv4gXsNMHx6CNPXpnBrfhYD/f1PaHON4MMOKDs46iNoIAgCUqwbsNZieWkBd5eX"
    "tshmg8DtBHSyOO47gEGCGvU/JHVa1zE1OYGHD+7DaD1HYC2CpEmlYbw0rJdx2jh9DNp4eLXz"
    "Fiurj9nuTnsk1VsYuSelhJQqIYJFSNR2P6I0duac1epzPp930aQQwh2KCFQayliKlHLC7+tP"
    "X7DtYpxesizCwc6BUgQYKG3x7sMnfD/4cZHaUuiEYla69KTUkNqQA4PdvS98VHbN7dpAigqO"
    "GK4Pf/5iNdAd4jSdlg7mdINAxJnpowCEAFdVqGYVc9le3t3vGkmEgNSaIKomyfjZIh/tJKEw"
    "QgswYRGaQE8mvU1T4T5Mi7Z0XP6q1SsXifYX52+wxUZ8NdibA90HR0CzzEJJzE1fQXF4kId2"
    "K4Z43hBOBTc0isR68kIZC7MzbPcocQlt5ngItcbJS1ncvj6Bm1cvPQ+vxtcEpGmiw65gbOQU"
    "yqNDmLl8Hj1pj72vEPC7o7r0j/Db1m9IXpOsR5U6siV8Af/3+SvAAF3qfL/KDVwgAAAAAElF"
    "TkSuQmCC")
    
vol_slider_ctrl_knob = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAA4AAAAOCAYAAAAfSC3RAAAAGXRFWHRTb2Z0d2FyZQBBZG9i"
    "ZSBJbWFnZVJlYWR5ccllPAAAA2ZpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tl"
    "dCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1l"
    "dGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUu"
    "MC1jMDYwIDYxLjEzNDc3NywgMjAxMC8wMi8xMi0xNzozMjowMCAgICAgICAgIj4gPHJkZjpS"
    "REYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgt"
    "bnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wTU09Imh0dHA6"
    "Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9tbS8iIHhtbG5zOnN0UmVmPSJodHRwOi8vbnMuYWRv"
    "YmUuY29tL3hhcC8xLjAvc1R5cGUvUmVzb3VyY2VSZWYjIiB4bWxuczp4bXA9Imh0dHA6Ly9u"
    "cy5hZG9iZS5jb20veGFwLzEuMC8iIHhtcE1NOk9yaWdpbmFsRG9jdW1lbnRJRD0ieG1wLmRp"
    "ZDpGNzdGMTE3NDA3MjA2ODExOTQ1N0NGRjE3REYyQjQ3NyIgeG1wTU06RG9jdW1lbnRJRD0i"
    "eG1wLmRpZDpBN0FFOEQ2NUU0NTIxMUUzQUFEMUExQTdCQTk4MjU0QSIgeG1wTU06SW5zdGFu"
    "Y2VJRD0ieG1wLmlpZDpBN0FFOEQ2NEU0NTIxMUUzQUFEMUExQTdCQTk4MjU0QSIgeG1wOkNy"
    "ZWF0b3JUb29sPSJBZG9iZSBQaG90b3Nob3AgQ1M1IE1hY2ludG9zaCI+IDx4bXBNTTpEZXJp"
    "dmVkRnJvbSBzdFJlZjppbnN0YW5jZUlEPSJ4bXAuaWlkOjA1ODAxMTc0MDcyMDY4MTE5MTA5"
    "OTM3OTYzRDA5OThGIiBzdFJlZjpkb2N1bWVudElEPSJ4bXAuZGlkOkY3N0YxMTc0MDcyMDY4"
    "MTE5NDU3Q0ZGMTdERjJCNDc3Ii8+IDwvcmRmOkRlc2NyaXB0aW9uPiA8L3JkZjpSREY+IDwv"
    "eDp4bXBtZXRhPiA8P3hwYWNrZXQgZW5kPSJyIj8+SxGGJAAAAolJREFUeNo8kV9r01AYxp82"
    "p3/SJP2TtE3dZufoOqXbUJh4450fQJjsC/gJBrsTRNkHcPgdvBx4IYjCroo3w8sxJx1zznZd"
    "bNMkbZP0T9pknpMLAy+cQ973eX7vcyKv3ryFPR5jc30dW5sbuLu0JPOJxI5pWVuadoN2uz3u"
    "dPUjs9//2jP7/mA8wb3VCojW66FGD2pahKHrexzH7SuyLE6mU9iOC6s/oNXfDWbeWaW89NJw"
    "R99HloloQc6B+D4ur/687xnGO8e2RZ/eqQDm8zlGoxHmsxmiJFaLxWLfHm+sPyvdKYHkUgKG"
    "jrMTJWQ30u2C53koioJkMokpdXVdF9FoFEouh4Kqxkuqeihms1VSzCswLGufNQ0GAzSbTWQy"
    "GVQqFTiOE7qqqorl5WUUCgVIkiQviNIeWVhcrPGCUJtMJuEgaz4/P4csy6HbysoK1tbWUCwW"
    "EY/HEYlEkBL455HTk5NtZzT+GAT+/52YAMMTRTF0Zvi3t7cIggA+rSQCjzCMNMVkYTC1GQ3i"
    "+vo6RGYi9Xo9FGD4bG/WJ/EJED6Vakw8Dx6t4XCIVqsVopbLZVSrVRwfH4d3hplOpyEIAjJp"
    "qUFcxz7Te3pjOBje1zQtHGSurImly/ZjooZhQNd10OeCafU/kcbFJWZj93XzRjvs0R8skHw+"
    "H2Ix9FKpBJs2s880TQT+3Ozo+gG3urGJZIw76/7t5G3HecKQWOwsReZKHz0MZUaDSxDOm8z8"
    "F23d+ME9ePgIHYrBx8gXjovaqVTqaS6Xi9MCPYeDhKMJ83zDmU63Ty8u64RwIIt5Gb9abdhD"
    "G0U5e6AUih+ymcw2TXJLoIMU2aPhHWmG9fnn7ys/LYlQRAH/BBgAXKNCHKfQxH4AAAAASUVO"
    "RK5CYII=")

vol_slider_ctrl_track = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAAICAYAAAA4GpVBAAAAGXRFWHRTb2Z0d2FyZQBBZG9i"
    "ZSBJbWFnZVJlYWR5ccllPAAAA2hpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tl"
    "dCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1l"
    "dGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUu"
    "My1jMDExIDY2LjE0NTY2MSwgMjAxMi8wMi8wNi0xNDo1NjoyNyAgICAgICAgIj4gPHJkZjpS"
    "REYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgt"
    "bnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wTU09Imh0dHA6"
    "Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9tbS8iIHhtbG5zOnN0UmVmPSJodHRwOi8vbnMuYWRv"
    "YmUuY29tL3hhcC8xLjAvc1R5cGUvUmVzb3VyY2VSZWYjIiB4bWxuczp4bXA9Imh0dHA6Ly9u"
    "cy5hZG9iZS5jb20veGFwLzEuMC8iIHhtcE1NOk9yaWdpbmFsRG9jdW1lbnRJRD0ieG1wLmRp"
    "ZDpGNzdGMTE3NDA3MjA2ODExOTQ1N0NGRjE3REYyQjQ3NyIgeG1wTU06RG9jdW1lbnRJRD0i"
    "eG1wLmRpZDo3N0M2N0VCM0FBNUUxMUU0ODREOUU3MDdERTc0QzUzMiIgeG1wTU06SW5zdGFu"
    "Y2VJRD0ieG1wLmlpZDo3N0M2N0VCMkFBNUUxMUU0ODREOUU3MDdERTc0QzUzMiIgeG1wOkNy"
    "ZWF0b3JUb29sPSJBZG9iZSBQaG90b3Nob3AgQ1M2IChNYWNpbnRvc2gpIj4gPHhtcE1NOkRl"
    "cml2ZWRGcm9tIHN0UmVmOmluc3RhbmNlSUQ9InhtcC5paWQ6MDk4MDExNzQwNzIwNjgxMThD"
    "MTRFMzg3OTBBMjEzQTgiIHN0UmVmOmRvY3VtZW50SUQ9InhtcC5kaWQ6Rjc3RjExNzQwNzIw"
    "NjgxMTk0NTdDRkYxN0RGMkI0NzciLz4gPC9yZGY6RGVzY3JpcHRpb24+IDwvcmRmOlJERj4g"
    "PC94OnhtcG1ldGE+IDw/eHBhY2tldCBlbmQ9InIiPz7ikfM3AAAAMUlEQVR42mKQlJA0ZRIW"
    "Fp7MFBYeZs4gKSn5nwEI/jMFBgaeYPj//382A1AJA0CAAQCqFwpCVrIPYQAAAABJRU5ErkJg"
    "gg==")

vol_slider_ctrl_track_left_end = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAAYAAAAICAYAAADaxo44AAAAGXRFWHRTb2Z0d2FyZQBBZG9i"
    "ZSBJbWFnZVJlYWR5ccllPAAAA2hpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tl"
    "dCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1l"
    "dGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUu"
    "My1jMDExIDY2LjE0NTY2MSwgMjAxMi8wMi8wNi0xNDo1NjoyNyAgICAgICAgIj4gPHJkZjpS"
    "REYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgt"
    "bnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wTU09Imh0dHA6"
    "Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9tbS8iIHhtbG5zOnN0UmVmPSJodHRwOi8vbnMuYWRv"
    "YmUuY29tL3hhcC8xLjAvc1R5cGUvUmVzb3VyY2VSZWYjIiB4bWxuczp4bXA9Imh0dHA6Ly9u"
    "cy5hZG9iZS5jb20veGFwLzEuMC8iIHhtcE1NOk9yaWdpbmFsRG9jdW1lbnRJRD0ieG1wLmRp"
    "ZDpGNzdGMTE3NDA3MjA2ODExOTQ1N0NGRjE3REYyQjQ3NyIgeG1wTU06RG9jdW1lbnRJRD0i"
    "eG1wLmRpZDo3N0M2N0VBRkFBNUUxMUU0ODREOUU3MDdERTc0QzUzMiIgeG1wTU06SW5zdGFu"
    "Y2VJRD0ieG1wLmlpZDo3N0M2N0VBRUFBNUUxMUU0ODREOUU3MDdERTc0QzUzMiIgeG1wOkNy"
    "ZWF0b3JUb29sPSJBZG9iZSBQaG90b3Nob3AgQ1M2IChNYWNpbnRvc2gpIj4gPHhtcE1NOkRl"
    "cml2ZWRGcm9tIHN0UmVmOmluc3RhbmNlSUQ9InhtcC5paWQ6MDk4MDExNzQwNzIwNjgxMThD"
    "MTRFMzg3OTBBMjEzQTgiIHN0UmVmOmRvY3VtZW50SUQ9InhtcC5kaWQ6Rjc3RjExNzQwNzIw"
    "NjgxMTk0NTdDRkYxN0RGMkI0NzciLz4gPC9yZGY6RGVzY3JpcHRpb24+IDwvcmRmOlJERj4g"
    "PC94OnhtcG1ldGE+IDw/eHBhY2tldCBlbmQ9InIiPz4xwvk1AAAAjUlEQVR42mKUlJBkgAJW"
    "IBYGYlEg5mCBCsoCcSc7O7ssNw83KyMDIwNMIlVMXEzHzc1Nm4+Pj+n///8MjFCjfP7++9vH"
    "wcGh+u/fP4a/f/8yMIAkgCqE5OTkZgIV/IdhmFF8ly9fXl9RUcH57NkzJSYmJmawUc+eP2ME"
    "SqoDsSIQSwAxJyOSc1EAQIABAOEHI1NO5Aa1AAAAAElFTkSuQmCC")

vol_slider_ctrl_track_right_end = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAAYAAAAICAYAAADaxo44AAAAGXRFWHRTb2Z0d2FyZQBBZG9i"
    "ZSBJbWFnZVJlYWR5ccllPAAAA2hpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tl"
    "dCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1l"
    "dGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUu"
    "My1jMDExIDY2LjE0NTY2MSwgMjAxMi8wMi8wNi0xNDo1NjoyNyAgICAgICAgIj4gPHJkZjpS"
    "REYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgt"
    "bnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wTU09Imh0dHA6"
    "Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9tbS8iIHhtbG5zOnN0UmVmPSJodHRwOi8vbnMuYWRv"
    "YmUuY29tL3hhcC8xLjAvc1R5cGUvUmVzb3VyY2VSZWYjIiB4bWxuczp4bXA9Imh0dHA6Ly9u"
    "cy5hZG9iZS5jb20veGFwLzEuMC8iIHhtcE1NOk9yaWdpbmFsRG9jdW1lbnRJRD0ieG1wLmRp"
    "ZDpGNzdGMTE3NDA3MjA2ODExOTQ1N0NGRjE3REYyQjQ3NyIgeG1wTU06RG9jdW1lbnRJRD0i"
    "eG1wLmRpZDo3N0M2N0VCN0FBNUUxMUU0ODREOUU3MDdERTc0QzUzMiIgeG1wTU06SW5zdGFu"
    "Y2VJRD0ieG1wLmlpZDo3N0M2N0VCNkFBNUUxMUU0ODREOUU3MDdERTc0QzUzMiIgeG1wOkNy"
    "ZWF0b3JUb29sPSJBZG9iZSBQaG90b3Nob3AgQ1M2IChNYWNpbnRvc2gpIj4gPHhtcE1NOkRl"
    "cml2ZWRGcm9tIHN0UmVmOmluc3RhbmNlSUQ9InhtcC5paWQ6MDk4MDExNzQwNzIwNjgxMThD"
    "MTRFMzg3OTBBMjEzQTgiIHN0UmVmOmRvY3VtZW50SUQ9InhtcC5kaWQ6Rjc3RjExNzQwNzIw"
    "NjgxMTk0NTdDRkYxN0RGMkI0NzciLz4gPC9yZGY6RGVzY3JpcHRpb24+IDwvcmRmOlJERj4g"
    "PC94OnhtcG1ldGE+IDw/eHBhY2tldCBlbmQ9InIiPz4IrLSeAAAAnklEQVR42mKUlJA0YWBg"
    "+ALEL4D4IxD/B2IGZgV5hXXs7Oz+P3/+DAXyGYH4KhD/Y87OyZ6tqKQow8TMJPry5UuQepDE"
    "KwYJCYn//Pz8IO3/mZiY4v7//88INJ6B5cULkNEMDEDBv93d3f+ATBkgfswSFBR0ko2N7beb"
    "m9vZxMTEt0DBzyCFjECtWUD6G9RV56QkpV6BJUDmYQMAAQYATncwTO8AX+4AAAAASUVORK5C"
    "YII=")
    
vu_meter_on = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAPIAAAAQCAYAAAAs5CItAAAAGXRFWHRTb2Z0d2FyZQBBZG9i"
    "ZSBJbWFnZVJlYWR5ccllPAAAA2ZpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tl"
    "dCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1l"
    "dGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUu"
    "MC1jMDYwIDYxLjEzNDc3NywgMjAxMC8wMi8xMi0xNzozMjowMCAgICAgICAgIj4gPHJkZjpS"
    "REYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgt"
    "bnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wTU09Imh0dHA6"
    "Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9tbS8iIHhtbG5zOnN0UmVmPSJodHRwOi8vbnMuYWRv"
    "YmUuY29tL3hhcC8xLjAvc1R5cGUvUmVzb3VyY2VSZWYjIiB4bWxuczp4bXA9Imh0dHA6Ly9u"
    "cy5hZG9iZS5jb20veGFwLzEuMC8iIHhtcE1NOk9yaWdpbmFsRG9jdW1lbnRJRD0ieG1wLmRp"
    "ZDpGNzdGMTE3NDA3MjA2ODExOTQ1N0NGRjE3REYyQjQ3NyIgeG1wTU06RG9jdW1lbnRJRD0i"
    "eG1wLmRpZDo2NkMxRUVCOUUwOEQxMUUzQkEwNkY0MDA2RTE1MjRCNyIgeG1wTU06SW5zdGFu"
    "Y2VJRD0ieG1wLmlpZDo2NkMxRUVCOEUwOEQxMUUzQkEwNkY0MDA2RTE1MjRCNyIgeG1wOkNy"
    "ZWF0b3JUb29sPSJBZG9iZSBQaG90b3Nob3AgQ1M1IE1hY2ludG9zaCI+IDx4bXBNTTpEZXJp"
    "dmVkRnJvbSBzdFJlZjppbnN0YW5jZUlEPSJ4bXAuaWlkOjA0ODAxMTc0MDcyMDY4MTE5N0E1"
    "RjI2M0E1ODNBNkQwIiBzdFJlZjpkb2N1bWVudElEPSJ4bXAuZGlkOkY3N0YxMTc0MDcyMDY4"
    "MTE5NDU3Q0ZGMTdERjJCNDc3Ii8+IDwvcmRmOkRlc2NyaXB0aW9uPiA8L3JkZjpSREY+IDwv"
    "eDp4bXBtZXRhPiA8P3hwYWNrZXQgZW5kPSJyIj8+8PUmPgAAEE5JREFUeNrMm39wVNd1x899"
    "P/btW2n1C7SsZMnIGGTjrCexxY8uFrWwjWtj2UEgGSeusIqIsUHpTJQxddLOZOKC5XHVTFrV"
    "2G0ST9sYMDVJwFE8McLJSOtSO3UTDCI1IDBgNY52haTVj32/7+15u09hJUzF7r4/usyZXZ7e"
    "fvZ7z73n3XPufY/4CwpgsvkkAQDbuLT36c+2pb/YLKOOpf5fIbO07+XMY4W8qzxym89VXv4j"
    "C9hkf9Q1nvDJr13VZ6xc6S4P3O2PkpICNjIy7hqPXgR3x9+RkKs8vmu+qzzHgJAdF3l8t01A"
    "E2cZn/YD6WDLMcMxHc0EkbMgHzs6TyCu8HhiMQ9h4CHu8CTOIiUCg2KX9HnwWAHqKwBXeMRQ"
    "LTIZZdzksCs8JssWDQYZDQRc4d0Gp6yvQhfbCt9zx3+pY9MDO3eeARYbx+CbdIk3KVns0jwG"
    "gyXu9O8Ib5EPZUb6vW75b9qHVHCAEpoXLQ8tH83n/N/j/ACXBqUOTENT0BJok8l3gscp/jMZ"
    "DwLx5Myzj7MkkcdveNzRxygYqE8kHvfai/oEF/QxagDhKRM8PDH13Hkch0PbokTTeCZJOfO8"
    "oBpjUISTXhW/EC6407+pv/POd3P0Hx7n8O8C8kwXeBT9J1AKss6D4smdh5dq8OD4K7B4GOfd"
    "8J86HdTTQWzDCtHmOVaMVuD8gMdxdPrVwQZMoY2jjaBdxkE9lvwBkvxh0RGZOw9c4nFkDJmo"
    "j1A8ywUeODxwh8csbC/OJRjNeEHOncfzqI+k2uuC//wwMeYBfRINRzaXuz5wuX8p8piLPJMb"
    "A4r+Y+74D3QcfxT12Rd+Am74z36PT58nOFcCG7IALO1G6VcdjfzoRyHQJ4qAcDwOBGJn4Gkz"
    "PcOxhoOXWUyeFzUr7+0zbnviaFqqYDjMEjC1SunItxv56H+HQB0vAo7nHdbM1CHJoxbLmx81"
    "q+/vM1a2XpPnPfytRu7T34aIksYjafoYu8LLL42aofv79NVfOYrHBTzvCo8hz0B9//SNRv78"
    "qRBMxVM8m0XS9DFHH0VeEfLC6/qM9U8jb5Y+m6cj73nkfdQfgol03mfos3nzkHcv8lq2Y3uJ"
    "4FwQnPaSJE98eU8jOXc+RKYmkXeN/qBOfxQVR+mqVX3mxo0z28sY6mPI0yu9O3c2cv0nQyQ+"
    "rQ+u1mdnLbb/SlFffX2fvqPtqAkC1iNMRDPwsxetxNLMyp075cb+fi4Uj5MijsNiiDgenDla"
    "KL5bpaUsWl9v9O3YoX9m/2oaZM8jDs+elYnD06Hy2RfkxpOnkTdBirC1fNJ5s3kpD1qBeSz6"
    "0D1G3/Zm5HHpPPQfYSWagbzDo439v9NDcYUW8Ry5Bg8l2vr8fPShz8l92/+4IMVj5Io+DvVZ"
    "tHLn2GBjv5EIxalVxME1eEmJyOPEaL1c2LfDv+CoM2tTJ9BNu0ZeiB+CRBm+xfvus1+lhYuW"
    "WeVhoPICmOvFjV8A8dwh/DXrmHL/DzqxRo6Bj9fBy8tEG67yvvn1Njrv5mXWTbVA/dfBu3we"
    "xJM/RnnmMeXx1zpxFo1hjaxjmi6TqViVfOBrbVYAeYtXAyu8Dl7sPAj/dRAItY4lntzXCV4u"
    "RgoFHfyobzJW5f3O9jZaUb3MuuNuoCXBuXn/cw7Ed15H16G+53/cidfOGOSjvjyQyVi0yvvs"
    "0210EfLCyFtQNjfv4wEQD9k89N8PDnYSQ4mRqRGdqHGZi0WrxBdfaDOXr1hmrVkDrKx8bt7A"
    "WRD27QVuZOSY/uLfdDKfL0bnzdNZcbEMY2NV8lPb2qxq1Fdn865D38AA8vYBwfaywwc6b4cT"
    "sS/DPr0eumVPdLBq+zZPW3U1XVZXZ0JZGZuTNzDAwb59IjYXjh0+nOjEQzEnNZSjUVK1bZuc"
    "Pe8Q8nSIsSnQmYK8IVL11DeRtwh5f4S8wHXwLnCw/00RTOQdekXthAkpxj4tQqpfjsa4qqf3"
    "j7RVB8Rldy/xQlkhPzcvZsDrH0yBSeHYT7Ys6CTDfIyckXTysUeOjtGqbZcvtFWL3mV1UgGU"
    "8eLcPFOFfYkRsBg7drh0yYt46BLakJ3d2IFcjR9u9EaeeZr5Ahu0mmcgoxdeL+S3N4O5qL7D"
    "CH05goGsYiD7vd1fa2H+QIN27zcz5Fkg//AxMENf7DCWN0cwkFUMZL984M9baMGCBu2hv8yM"
    "Ry3wvfIomHeu79DveSKCgaxCPur77lMtbF6wQdvy7Yx58rOPgFm3scPYsCWCgaxiQuT3fmNb"
    "Cwsg75kseM0Pg1m/scPcsClCEqMqBrLfs+u5FisUatB27c6Mh6Pa9+ADQFeu7DAfeyyCgayy"
    "oiK/d8f2FhosQ96uzHnrHgSh6ZGO0NY7Il+C/eoD8HP/c1ujLeVBq2HXLjVTHKxblwdNTUbH"
    "1q16xEkb/Vu3yi3BIMue14i8zXoEA1nFQPZ/5Rm5payUNTzXniEP57j6P8uDxgfNjtYH+AgG"
    "sgrD+f4nXx1vCfr5hufqizPmPfzKEDTentfRurg4Qk5LKrko+rdeuNQS5MWGXYUVmfFwSl8X"
    "PQMbfMW7t+UHfo6HBu1Um5te7OI/fX+1saQJMn4RDszFG0A8/7M6TAgkNDvH9/IX/r3W+MJj"
    "WfB4MD//KIin3kzxwOENvFtrrPhS5jzMRo3lj4Jw/FCdsx6Q4n3YV2v8SXNWPHPt4yD2/mgm"
    "773eWqMpS95G5HVP81iSx/3mN7XGEy2Z8zB/NJqbgf/lL1I8QlL6elFfyxNZ87g3flTHAZXQ"
    "kry+Xq62pUXPBgfNzTq88YY4w3+9vUJuvIMzeX3vCbWbN2TBw4h4vEGHg28hj5Er+s6qtZtX"
    "5mfHW54HB49PIQ/1MYenTtS25M3PnIdB0Yzf+7fEyJq0eprj/rAXxfEGmCpk9TITWD15teQK"
    "s11T2gtAnIA8LTuePoXVu8ObXrmzeUZ2+oiewGpH1tL23yjwyNOybK+K+iTf1Tw1S14CebLX"
    "4RFG7HbzXNY8MjWFXSyleHbNay948di/Spa8ySkgPq+GnWAvdDEO5xkB41tRSFa8yUkCPh/M"
    "8B+fK0++mqdq2fGmEgRkCXmEpXiMUIEjhmqw7HgaA1kkWjIuSIqHxb+hsOx4k3bWSjhteg/Z"
    "fuecxQbVLL/rl57jXalF00w6WYuD57f/Ckb1piNOmmQHoGreXNfr6ftOMlXOiKeMgedXr4JR"
    "86dXeLa+W9b0Skf+NpmKZsRLjIEY+T7o4c0pHnP01dzX63nthcx5E6jv0MtgrGuZyVuNvL/v"
    "yJwXHwXPv7wCxqYtyCPJ9jJCVLpiRa+0669TuWMmvNFREF/6B7AeedjRx1AfU821a3ul3buy"
    "4+15CYzW1iN4RVAt4DULBPW+tbR3924pUxyMjhLYs8cDra36jP5du9Z0l7caeS9JydQ2I16c"
    "wMs/9MCWTQ6PMDug1ftu9fY+/3Y8c16CwsuRCWgN+1M8DnkcU9fKBb27479LpsoZ8agJeyai"
    "8GR+4G2nrWbyRieskSuTK9YAC+WerV/H2TVslYWB5V3HYsjYORA+eQdo0eIe5d49XSByw1gj"
    "a5jI+bCuDcr7mtvBQF7VXcAKr2OxZngAhNNHgJZW9yibvt8FHBnGGllDlg84CPq+93g7ztZh"
    "a8lq/M3r4A2dBeHU20AX3NKjtL7ahQnrMCkQNKyRfeBBfX+1sR1n17D1hbuBlc5dq3CXToPw"
    "3ltAFy7tUb61twsTpWGskTWQsUoWISi3Ii+BvDDyym6Ym3fuDAjvIG/JrT3KS691EV0ZJokR"
    "jajjPmLqQc+zf9HOBD5sL07Risq5eac/AqH7pwBlZT36rt1dLC9vGGtkDWtkH/N4gr6G9e0w"
    "ifrW1CHvOtp7Gtvb3Q106dIecuCfuz4Px4exRtawRvbdCBeDG9dL7TgbhtesMaGiYu4Befo0"
    "B93dAixdSnsOHEjgrIH+Sw1Ge9sluH69L3ve68jTYRhrZA1rZB8O72DDNl87zq5he7GrIngd"
    "vPMc/OwXAty6mPa8/l21Cya8w1gja1gj+0AVgxv+MdY+pdOwvdhVUSTMzYsa8Fa/ArcGxZ79"
    "zYEuEhOGyRlJwxrZB+N8cH30bPsko+E1Xj9UJLeV5+BhRtqNE91SUe45MP/mv8NDn6BF7W0p"
    "O5DnO/tYpWg3iOcOhfnfv1+DM22AEcGT3PKwC+H01S1KTUINjeYFB82b6iPWgpoTmDIMYSDH"
    "MZBNDGQJg68ITy4XTxwM8xf/o4YoyONQLUluyXBp2x2Y/lkmsZBXUD5ohr4YsSqXp3gciTOR"
    "mCBircJBivfBG2H+3LEakogHMF28Jg9MAwdw+aBxx/qIddOKFM/LxTGQTfCjPhH1EeQd3R/m"
    "T7xbQybHUvp4/ur2WqgPebT0hkGzbmPE+lw4xZMgDnmoz4efBEjxfoK89yM1ZBx5vOO/2fps"
    "/xm6RssqBs2HkLcMeYwOYbIVJ4lRE30lYSBje1k5f+RImPvweA2ZmEi2l30GjyAPTFNjpYFB"
    "6541ERq6/QT+7hDz+eIYyCYGssQkCfWRcnHv3jAf6avBmTYAgpBq72x92F7QdY1VVA4aTU0R"
    "a9WqEzIoQxjI8UY4aNZDt7QQLuBQNsv37hXDkYhQgzNjQBDAk9ziIYy7giMUZ1lT10GrqKCD"
    "TU1GZNUq64Sz2hp3ZhS7Fk32b9Y8hjwd4iwBJpqE1CRv32Hk/Sfy4sjjr80zsNC6oQx564xI"
    "+E7kUW4Ixr1xNlRoQswvgSIW4bxXvv+DqXBkQK0ZVWhA4JCX2oLi0m7DohZlpm4xDYN9sPGO"
    "vEj4JukEmGSIDPNxclYyycceCSb4Iky0y/dOXQ5HtImaUWoFBII8+AweIA8zKwz2wSZfSWSV"
    "lG/771Nn1d/2YcIO5Hxnc9rvBHSJ49T8/2ODWnPuLBl3NvZHcBDHMZAVkHlM4HnR3jLKiWcL"
    "5ImCgWxh0InYNDlnfRKnkELU5xdEnJFz53lAwRnZSs7HYo76GI1jFaZgIFtYXuDlS8uNx3Fx"
    "JssKBrLFiotF5vXmxPOCGr8NTimb4ID1MPxUXAJncu/f1J1KlrOfnKP/kGeAgjOyhTOyiJ9z"
    "41ESh0mvwn5faEHUL0JCyo1nkTi5zCsYyBY57xFhjM/Vf/b7hHNcF5x9PHCujJpzsuxs0ovO"
    "qjY3YwU8da7u1CQJ5/Y4xTk+fcudmhMPXObZ+jiXecRFHsGLIKPu8SjF9nKu8VTwKhjMSR4H"
    "9P9f/xLkMYfHXOBxeDmgxNFHcufxyLOIe/pS/tOcNa7kvdamE/nTgTwxC8jNuveTpd9R4oBS"
    "N3DrmAV4UaOQvFNIz5lnMXs2ts92h5dAfXmoz+OSPhWPyclvu8JjUr5F1AnA2dgVHqbjFhQW"
    "As7GrvCOwV3WfXAUboYBd/yXOgbOnX658yQ8lro8uMMrSlhwGSfKhMed/i0zLHIJvxrn3fRf"
    "8mkoYj/GmFzSbj6Z/hjVbLvqto1ZP5L+COMf1kpy5TmPMLrGcx5hdI0HiwjLDwVS/uuP5sxz"
    "HmF0TZ/zCKN7PHC3PyD1GGPyhJGR8Zx5ziOM7o2/1COMrvGcRxhd45UM/pqNVNyZPOF/BRgA"
    "eSAgQKFYb0EAAAAASUVORK5CYII=")
    
vu_meter_off = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAPIAAAAQCAYAAAAs5CItAAAAGXRFWHRTb2Z0d2FyZQBBZG9i"
    "ZSBJbWFnZVJlYWR5ccllPAAAA2ZpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tl"
    "dCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1l"
    "dGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUu"
    "MC1jMDYwIDYxLjEzNDc3NywgMjAxMC8wMi8xMi0xNzozMjowMCAgICAgICAgIj4gPHJkZjpS"
    "REYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgt"
    "bnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wTU09Imh0dHA6"
    "Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9tbS8iIHhtbG5zOnN0UmVmPSJodHRwOi8vbnMuYWRv"
    "YmUuY29tL3hhcC8xLjAvc1R5cGUvUmVzb3VyY2VSZWYjIiB4bWxuczp4bXA9Imh0dHA6Ly9u"
    "cy5hZG9iZS5jb20veGFwLzEuMC8iIHhtcE1NOk9yaWdpbmFsRG9jdW1lbnRJRD0ieG1wLmRp"
    "ZDpGNzdGMTE3NDA3MjA2ODExOTQ1N0NGRjE3REYyQjQ3NyIgeG1wTU06RG9jdW1lbnRJRD0i"
    "eG1wLmRpZDo2NkMxRUVCREUwOEQxMUUzQkEwNkY0MDA2RTE1MjRCNyIgeG1wTU06SW5zdGFu"
    "Y2VJRD0ieG1wLmlpZDo2NkMxRUVCQ0UwOEQxMUUzQkEwNkY0MDA2RTE1MjRCNyIgeG1wOkNy"
    "ZWF0b3JUb29sPSJBZG9iZSBQaG90b3Nob3AgQ1M1IE1hY2ludG9zaCI+IDx4bXBNTTpEZXJp"
    "dmVkRnJvbSBzdFJlZjppbnN0YW5jZUlEPSJ4bXAuaWlkOjA0ODAxMTc0MDcyMDY4MTE5N0E1"
    "RjI2M0E1ODNBNkQwIiBzdFJlZjpkb2N1bWVudElEPSJ4bXAuZGlkOkY3N0YxMTc0MDcyMDY4"
    "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"
    "LeKpAAAAAElFTkSuQmCC")

#----------------------------------------------------------------------
rec_txt_left_end = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAA8AAAAaCAYAAABozQZiAAAAGXRFWHRTb2Z0d2FyZQBBZG9i"
    "ZSBJbWFnZVJlYWR5ccllPAAAA2hpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tl"
    "dCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1l"
    "dGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUu"
    "My1jMDExIDY2LjE0NTY2MSwgMjAxMi8wMi8wNi0xNDo1NjoyNyAgICAgICAgIj4gPHJkZjpS"
    "REYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgt"
    "bnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wTU09Imh0dHA6"
    "Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9tbS8iIHhtbG5zOnN0UmVmPSJodHRwOi8vbnMuYWRv"
    "YmUuY29tL3hhcC8xLjAvc1R5cGUvUmVzb3VyY2VSZWYjIiB4bWxuczp4bXA9Imh0dHA6Ly9u"
    "cy5hZG9iZS5jb20veGFwLzEuMC8iIHhtcE1NOk9yaWdpbmFsRG9jdW1lbnRJRD0ieG1wLmRp"
    "ZDpGNzdGMTE3NDA3MjA2ODExOTQ1N0NGRjE3REYyQjQ3NyIgeG1wTU06RG9jdW1lbnRJRD0i"
    "eG1wLmRpZDpERTM4RjAwMUFFODAxMUU0OTk0M0RFRENDQjJFMjVEMiIgeG1wTU06SW5zdGFu"
    "Y2VJRD0ieG1wLmlpZDpERTM4RjAwMEFFODAxMUU0OTk0M0RFRENDQjJFMjVEMiIgeG1wOkNy"
    "ZWF0b3JUb29sPSJBZG9iZSBQaG90b3Nob3AgQ1M2IChNYWNpbnRvc2gpIj4gPHhtcE1NOkRl"
    "cml2ZWRGcm9tIHN0UmVmOmluc3RhbmNlSUQ9InhtcC5paWQ6Rjc3RjExNzQwNzIwNjgxMTgw"
    "ODNDQUE2MUI1NkU2NTkiIHN0UmVmOmRvY3VtZW50SUQ9InhtcC5kaWQ6Rjc3RjExNzQwNzIw"
    "NjgxMTk0NTdDRkYxN0RGMkI0NzciLz4gPC9yZGY6RGVzY3JpcHRpb24+IDwvcmRmOlJERj4g"
    "PC94OnhtcG1ldGE+IDw/eHBhY2tldCBlbmQ9InIiPz7nL34XAAABqElEQVR42pyUzUrDQBDH"
    "k81qiqGUNB4D9mYriBbEk1B9jF6EHPpUPbQn+xAFbwWh0mtAL8WTpJKCEkyISd0JHZkuSUhd"
    "GLLd5jf/2fkI22w2yn+NK2RNJhNDPC6EnSoVFpd+d4bDoeO67pWqqgpjbOdPOAPDPZNgdzAY"
    "PNi2/YpgmqZ/liRJZrjfgfv9fgAOHMd5rNVqAZ7D/agTNFkZHLybpvnU7XafQR3Cy0sWLFaQ"
    "C7fX671ompaCA3SC98VocmGhHlmW9dZsNj3hQAFDB+gsOyuphC/gDwTlCMB4CfzVaDQ+UQ2T"
    "lt1166QMDg3D+KZKtMZ5daYr4Zz/yIc0aWVwrOt6XNaeZbAWxzGjdcUSVYEPoijS8WUKVYHr"
    "6/W6jlneFzZ93z8uCrkQFnOtiqlprVYrG4dgH2V7NpudiIQdyhCtdVGTtBeLxbmsSsG8LwmE"
    "3JnP59ee57VoN9GhyO1tAVphGN5Mp9M7BGEwKEgdcAIeQbij0eg2CAKLKuBkyeNJldvj8fh+"
    "uVyeiZ5WwPBl3MNzRx2TsVW+rPrZza6VV7+q61eAAQBAdAcpb5vsTwAAAABJRU5ErkJggg==")

#----------------------------------------------------------------------
rec_txt_middle = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAAaCAYAAAB2BDbRAAAAGXRFWHRTb2Z0d2FyZQBBZG9i"
    "ZSBJbWFnZVJlYWR5ccllPAAAA2hpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tl"
    "dCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1l"
    "dGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUu"
    "My1jMDExIDY2LjE0NTY2MSwgMjAxMi8wMi8wNi0xNDo1NjoyNyAgICAgICAgIj4gPHJkZjpS"
    "REYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgt"
    "bnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wTU09Imh0dHA6"
    "Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9tbS8iIHhtbG5zOnN0UmVmPSJodHRwOi8vbnMuYWRv"
    "YmUuY29tL3hhcC8xLjAvc1R5cGUvUmVzb3VyY2VSZWYjIiB4bWxuczp4bXA9Imh0dHA6Ly9u"
    "cy5hZG9iZS5jb20veGFwLzEuMC8iIHhtcE1NOk9yaWdpbmFsRG9jdW1lbnRJRD0ieG1wLmRp"
    "ZDpGNzdGMTE3NDA3MjA2ODExOTQ1N0NGRjE3REYyQjQ3NyIgeG1wTU06RG9jdW1lbnRJRD0i"
    "eG1wLmRpZDpERTM4RjAwNUFFODAxMUU0OTk0M0RFRENDQjJFMjVEMiIgeG1wTU06SW5zdGFu"
    "Y2VJRD0ieG1wLmlpZDpERTM4RjAwNEFFODAxMUU0OTk0M0RFRENDQjJFMjVEMiIgeG1wOkNy"
    "ZWF0b3JUb29sPSJBZG9iZSBQaG90b3Nob3AgQ1M2IChNYWNpbnRvc2gpIj4gPHhtcE1NOkRl"
    "cml2ZWRGcm9tIHN0UmVmOmluc3RhbmNlSUQ9InhtcC5paWQ6Rjc3RjExNzQwNzIwNjgxMTgw"
    "ODNDQUE2MUI1NkU2NTkiIHN0UmVmOmRvY3VtZW50SUQ9InhtcC5kaWQ6Rjc3RjExNzQwNzIw"
    "NjgxMTk0NTdDRkYxN0RGMkI0NzciLz4gPC9yZGY6RGVzY3JpcHRpb24+IDwvcmRmOlJERj4g"
    "PC94OnhtcG1ldGE+IDw/eHBhY2tldCBlbmQ9InIiPz4NEjm+AAAATUlEQVR42ozNsRWAQAgD"
    "0IBQ8G4HWua65VjHiXh4pxaWpvhFUgTdjSMiJtz95KoC7+4BK7zyhYhe7vUHIgJWVbCZgccY"
    "QGZO7I9LgAEAZ2ET2vWR68UAAAAASUVORK5CYII=")

#----------------------------------------------------------------------
rotary_knob = PyEmbeddedImage(
    "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")

#----------------------------------------------------------------------
click_bpm_ctrl = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAF8AAAAeCAIAAADFKlVrAAAAA3NCSVQICAjb4U/gAAAQn0lE"
    "QVRogT16u7IsS1LlWv6IyKxzG/gERhgZZVpDhbFR0Gb+GQkdAdBHoK25Z+/KCH8gRJ1WttW2"
    "ysr08PDw9fDk/OM/2c///Os//QdUzSwzAXQVRUjW3gBoBqBjybhqvWnD3GNvigCoTJIdIWNU"
    "JgBk+nVFBAAA3Y3cUFezjDCzeB4AdCd5fg4S3edvR0AEVecCM1vPIyIgzw0rAlUyRlf5GOt5"
    "kAlVNeuqBkQkI9A9rmvvLSK5NwCQ7r7fbwAQQQXU/xL8WXh3o9vcM9OuXj/+9G//8x//b+39"
    "KwtxbkRVEVHVtRZiw/ysXMfITJJyslMlKgTj/X3/4a/WWiRjbxCkmNl+v8d9R0RVkexMHZ6R"
    "AFBF1e5G15jX+v4e993dJ7Odqe65t40R72+dV0aAVNPcAVJVu5vkuXNlAk05N2yQiA1RqnYl"
    "qnWMkyaq/qUIukpU/xIbKgFAbcxpf/Of//Y//vf/+5d//mcQw8deT1UCGGOuvdEFCmL7/YpM"
    "NLrCx4xIVYm9IEoQhFCqqzPm9dqxSZ7EdZXP2Zmxl89r721mEUGyM0BBl9oAkc8DUQgp0tVm"
    "GnuDRAPoswAAqDy/opqIEPgUaReAef94vn/6mPv7C6qk9NnROTMCXajy+7X3RqWYV5xkmYhU"
    "Ve+l88q9IPp3/+uPsp8nn2817YyIKAAUtbHWc54HgGNGZO8NQn3sveVXatB9rslY58OOXZlo"
    "ZERnmNl+nm74mHtvkt1ABCF+3aJ6//grCjMCqhCisjMpn0Nk7uOa6uOkRkQphi5Qe+/cK56H"
    "IuYOivp4fv5uY+71gDQfEEEX0FWFLvNBH5mJagAVSTGqCyWfp6uhnnudB6mqgIRY7C3mJEyV"
    "InXyUq0+1LwzSJEx5ETdZWqAmKqP2V0AzUdXo7pig2w0MtRH7IWurPxsl1pmcIzqjB0A3t9f"
    "uRYpaqbmFCOAiNxbzPJ59rNqPe6DlIrVOPvRMgYoft8g4/0GWFlQjfcbFACqJqIQhZq5QzQy"
    "u0rNaDrvH0Ddr5eZUgVCoMUU1TquyswIEVVUolGRVZ8q7SqIwiwjgAalcokIiIiA2vP1O4Sx"
    "V6PFTE0jEwR9QHTM2Q3YyOeBGNVZ5e5ioyLYQJaKirBBGy4+IARFSAihRnNQOsuuG4CMGZnn"
    "CJiZ+iClsyi6nzdAu26KdJf58PuGCNQis9GggLK/voTqPtgdz0L1+v4i9fv3/wJYmeJDzUih"
    "KrrMfcwpFQEzqvg1K9e4LoqSIqKsMh+VRQqplV1ZBOeYFJ1jjvtVmd2dO8yMoLmxqjLRTRG7"
    "fxAAoWNWQ1QoImYgq6pBErGjupFZEVmFBrJEDSTAzKTqB9cAimZWN9CNLmRQfbh3NwB2514R"
    "4WZUra6OJCGqVOvKzIQZusSs0VD1+85MihKs6k9rAzNiPY+h6r5fAOL9plgc5OumCMfs0wVV"
    "ATbK3CNiPQ9U1/v70x19dC3KADKeBxRSUEt9ZB5k8arsKmRD5IOmQEf4/arMzM0xVLWrs0rm"
    "AKDuABqotUB2t5oDaBGCUOsuNe/K/Ys6gCJmFAXhLtWwIc961KxVM6KrThsVVYyrqjILIg2q"
    "auVCJah18JQUiGSmiOq8T8TdQFdlull3Q03MbAxQqAbAxkCDPmSMsyqYdwMUnZddV+yAWncj"
    "C0B1ipq6o1vdVI0UUaNorFV7ixrWysgGxKyzurvW7u7Ouu7XuG5mVVethUbtXZlVFXtFBFUB"
    "fhgQQGGsvVfk896RIhbv76oyd5qBJJk7zMdBVVShKyPEjOYUoTtFkClUXWuJau5FM/oACXOA"
    "2ehuqjXYAMn9/eXzAggRiPQOZOfzJlhV47rqeeezxn2LeVfpGARRIFDPoiqbFAGaBESoqnO6"
    "D/igiKp1NTK7GmadBfSz997bXy80oNpVdl3iSlUIxezAG9EEUU3K2U6KdcThG0I5u2VjmjnI"
    "/XyzMealPs5B9jkPBFOEbhCRPkwXIAiguyjKhg23wwVVkVmRqNY5I6O6eMobgKpcN8h5XZkJ"
    "H3pdkdFVNAVJd1Q1AXdUi2pEnIyP6zp8bO0FEJSsoircT2GDhChVRDWqQNJMx4iILiBSqF1d"
    "O0QVNmpvHSMyDocUd5h1JNwKLWo0a2DvLaoQE/esyqqT5fU8EKFpZ3YWCDmssXZwfJq2qgDI"
    "qmctgN0NkKafiBsUBdiVel/oJsXn9azVaDXP5wHF50XKuC5RgWpFgoTqXosiotpVp9y6G02Q"
    "BNHdmWigCtWoIkXFqkooyDxa5Hyge1Uik8MrwsbgHA2gOtYDkQYoInOcAx4RXVWxxfTEUN1V"
    "eRh/dyNTzTtL3W1MVROSJHUMZFaWumcWVMeY6A9DpVnvGK9XRVCVJEXUR1dTVc3284DoHSIK"
    "c1Nb379X5Pv7nVmoAghwXDdVO6K7CWTW+vqqtdTUzD7gQlI4Xj/UjWbXdWWlqoKgasamiF3X"
    "L9ZDiKIBtW702rWDZmiquap1VkX5/UL2vC4xJ6VWVHXvraZq3lWd1XtzeGWwK7My1hhD+iiU"
    "vQlSpXaYufvY7weiIoqqMaeMud4PmmjUWhQB2VVdvb9+0oRH1sQmyt3G6zd2khDSrkvd2Lnf"
    "3+YuY/RHIrTOa/z4UZFHN1UkRAHuvSsSGc/zCKWq+5Niue+7uisbXepOERElGmiq0tTNzqHM"
    "2FQhOmL7fcWOzgRgcyIWfdTanxQDMifBed/w4cNRyEw5epNmUEGDao3ODHG34SRszozo2FSV"
    "0xHMzKyycKizOZoA6QPVoH7/15+7mmOaefdfUFlpHhGdJWMAPDi9fv5+FiaUcU10H31LVdjo"
    "3LXfonLgFVXfX9+dRdLHVVkUOeerG2c7I9Pm1X14AyF6ml1FiBtEqwo2KARFRZGboujuxvP9"
    "7eaxN80i4iOyVc3HVDUIDzZTWFl7rSayiu4AKESVj7G/fx5aAxV0+3AIQNLVh0M91wOwugHU"
    "2lCjqrmdRYqomB5tCVFxb1RWRgYEEFQXhTYMovSrIqvS3IEGgYzu2nF0n5q7XhcIdWt0Z2Vl"
    "oXHMA2F1mxlUjp3QleZWa9F1R+h1d1fHohDkL41m9VESJxsi3a2iogKiskRF3JRKEJk8VaaS"
    "kbTRewNCEVIiEtmIRCHWosDmhYNcXTLGabj7/SCDld11+l2tZWMe1tpArUCTJLKqOr6/QelM"
    "dTMfhwTc9y3zoqiKkpJRsXbuENHK6kh16/i09srsKlSRVFVEknLAERSsOJtn5hRD95hTzZlV"
    "1RCRfB45K1zrY5F0qyqJIw5iP+c0gaiDYrHHnHbd6Ebm5zioQsSHU+267tzr9YffzM3m7L1J"
    "MVWibUyIVNZwhwhMSYpJd/MwVtVeW9xYadfNLqiQ0t0iIqbP2qdXdrcdB+q4aBEiAmFlnnaj"
    "cwIf+RKRpFAIgkIBdQy4E9A56/hBVRHRaB2jqxBbdM7MdDcdTsCGiwiq1OxYXPN6UUnQzKHq"
    "7iAjoirMDeD6+vkx7si9w93e32+ovd9P7F3d51RmFUQic8yJyvfPrwPbEVHZZgoemikAuppm"
    "JH1ONwO6UXsvFe0MdPXeHYtkVdZe6EJHVVLEx/gA9tpqNsc8tKyqIFJ7C2UMBzCGU5j76dg0"
    "9+vqrEaLCLphLiLi7m4mgJqpCDLMBxpCmXMAMDVVyUwxO1SwGyJWkaJi162mzK2qQsYOc9fP"
    "NdpZZioicwySQu7vL4rqnObuY5gZuivL1NAd6wFJNGLH3mjo6aMFNCqLqj6njkEyM02NaL8u"
    "6mBDRXOHUPRgSCMy2RARdLHSxnD3Y0dk5GHP6sPMMtLHkEZFHLCSzFxrRaZ0n9Ok4+oqVWXF"
    "XlFdR7myg7GF4nNKBarGHKrWkaZKGwBE5BAWETlJEUB4YDVsDKL9fs1roqqyjl855+iIjFA1"
    "qvl1UUR8mnlVqYqKiAiONK/OSAp1TDUFoPMCoKZqpqZjju7qajVFJkGSXS2gXbebZabKhwZ/"
    "Aj4GAAlC0DQdc3aVCYnM4bYBVtVaoiqiPsfzMKt6b6X4HItEhKrk3jKmUKr7mD5V7e4i3O9v"
    "mncmRQGoKk37bF2ViokPAPG8fV6nd0REPA9FKcKKMa7Y230AyAyin/cbFBImLFD0A6uHX0GP"
    "P0lUvV6v7+c5WUYloCI4EXaXqAA4w4I4YuK4KyJ5NnuM7k41kLUXCIvnodkco7u7Fe7dXd1r"
    "bVVVM50zq7pbuuGDJFSFMoevvfNY1l0fq2NcnSnuHY+Ou6tJZpa5134qS02rmj5EJHY0oWqn"
    "gmhqOo6/e0SLHFM9Al3qAwCqWN0iBCji8/WsJaIAKmPt/bEQABHPzB4XALqbSHd3po6xI8z9"
    "FE7ubWYdS8bEZ9SgY4wlQor5fR8sd5ECQdTaFNEj4U13pJAFqLuQFWEEhPt5xI1d4sNM1/uN"
    "BlDjx/28n+v1hx2hqvk8cpY+rl+VXEZttLl92JY7RVQ1M3MtM3WzrDIyM6tCfHYVq+acJ5gz"
    "WulMd0NDRKrL3PNMezI7Qkx7x3y9np8/qaoiMAMwx6gqd8tIqtbe5hOAmlX38ZXmGF1lmVlV"
    "Zqpz7LUrM8dwYVaVkOA1RlZyh5qRaNXcC90Qimi5IDZU1VxE1LSyxmf3xEzdf+y1RaRinymK"
    "m30qHN3g+MUzM2u4b9JUI3O4g0D3eP2WmUWKu5mioQTd1rN8+N4BoZlFd1X5HGjA/YP6YGXO"
    "H6/p/qz9KVKiSET68EpllZgdVNUqFaEw1wZpFWFmc4zIVFKGa3XtRbUW6Ug1rV3juk57FqWU"
    "gYAoKt29CKpcc6y1eweB677W2vOaO0JAJ9Ft1wXwkKmIuK6rqo48r+6uNhVRAQ2RbqYq1f0J"
    "rMvHQCYibc4zGTzpczMRafR9XbEeFc1MEt1FNIb3jjnn8/VFM1c7JqKbZOVw34wusLJFTVXc"
    "RUCKm6mqgdzfX1J1z7lVq0pE1q8xXnUjtpuaWawNdxXZVFXJLGT78BouwH6WIvW+AOR6z3nn"
    "3kaiU+bkLyJTVbUfsynCbjlG8jAFEM/ToHW3AirdLZlQu6+53kkRAXV4d2eWqqh6ZlHRsUVN"
    "TcnJbpsj1yPXdaaA4p7Pe5jSXchcT6u5W6Z05uu+n+chqSJZNcbICFPJ7tzb1EzGvF61I/zX"
    "pPiQpdi7YDTrvVA95xC1tdZ9z/0sN60+AxCtyHlfpxAaLbx9eJAVoWN2df/SlnFWMoxgPG8B"
    "4I7Yrfbjtx8rslXVDFUU7h2mCmCYi/vRvPk8r+s6hNtUG02huhdIYVebm8wZz7tVTHUMD1OI"
    "1FpH04lZZdmhUiLX8GqM4bG3COd97efbxEDyD3/3D3/z53//27//P8cxPMvoblUFkHv7nHst"
    "dKNivH5b7zdVey+o3a/X8zyqut9viCC3zjufN8zd/SS61lvnLSr7/ZzjfR5xvoKNQzfMbL3f"
    "R0Z9f32NOc+8NCNQddQ5RMace++uFLWTax9jP8vcY60z2q6qc3hVNeO0S8ZaAMSsjnkiYmbd"
    "nc/70KXMFJGKAImPpfVw/vGfrl6//f9/7cwzxvcx9lrIPArgjNwjovf+TBQAde+qM3o/I/qu"
    "6ioxO0vyMdD9GX5WoULnnWdAHIs2ukoPe1jrNPBPZJlQFVUhP/oD6ExUHd2UzyPuJ1Qh43nG"
    "67Xeb3OnyMd7PG8ZnFceTsr2ljE+JFjkSNMzPj7/njcduuoTgAjI/wZ+yzqnq1Yn9wAAAABJ"
    "RU5ErkJggg==")
