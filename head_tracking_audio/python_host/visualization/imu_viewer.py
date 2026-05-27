from queue import Empty
import math
import time

import pygame
from pygame.locals import DOUBLEBUF, OPENGL
from OpenGL.GL import (
	glBegin,
	glClear,
	glClearColor,
	glColor3f,
	glEnable,
	glEnd,
	glLoadIdentity,
	glMultMatrixf,
	glRotatef,
	glTranslatef,
	glVertex3f,
	GL_COLOR_BUFFER_BIT,
	GL_DEPTH_BUFFER_BIT,
	GL_DEPTH_TEST,
	GL_LINES,
)
from OpenGL.GLU import gluPerspective


def _draw_axes(length=1.5):
	glBegin(GL_LINES)
	glColor3f(1.0, 0.0, 0.0)
	glVertex3f(0.0, 0.0, 0.0)
	glVertex3f(length, 0.0, 0.0)
	glColor3f(0.0, 1.0, 0.0)
	glVertex3f(0.0, 0.0, 0.0)
	glVertex3f(0.0, length, 0.0)
	glColor3f(0.0, 0.0, 1.0)
	glVertex3f(0.0, 0.0, 0.0)
	glVertex3f(0.0, 0.0, length)
	glEnd()


def _draw_cube():
	vertices = [
		(1, -1, -1),
		(1, 1, -1),
		(-1, 1, -1),
		(-1, -1, -1),
		(1, -1, 1),
		(1, 1, 1),
		(-1, -1, 1),
		(-1, 1, 1),
	]
	edges = [
		(0, 1), (1, 2), (2, 3), (3, 0),
		(4, 5), (5, 7), (7, 6), (6, 4),
		(0, 4), (1, 5), (2, 7), (3, 6),
	]

	glBegin(GL_LINES)
	glColor3f(0.9, 0.9, 0.9)
	for edge in edges:
		for vertex in edge:
			glVertex3f(*vertices[vertex])
	glEnd()


def _normalize_quat(q):
	qw, qx, qy, qz = q
	norm = math.sqrt(qw * qw + qx * qx + qy * qy + qz * qz)
	if norm <= 0.0:
		return 1.0, 0.0, 0.0, 0.0
	return qw / norm, qx / norm, qy / norm, qz / norm


def _quat_to_matrix(q):
	qw, qx, qy, qz = q
	qw, qx, qy, qz = _normalize_quat((qw, qx, qy, qz))

	m00 = 1.0 - 2.0 * (qy * qy + qz * qz)
	m01 = 2.0 * (qx * qy - qw * qz)
	m02 = 2.0 * (qx * qz + qw * qy)

	m10 = 2.0 * (qx * qy + qw * qz)
	m11 = 1.0 - 2.0 * (qx * qx + qz * qz)
	m12 = 2.0 * (qy * qz - qw * qx)

	m20 = 2.0 * (qx * qz - qw * qy)
	m21 = 2.0 * (qy * qz + qw * qx)
	m22 = 1.0 - 2.0 * (qx * qx + qy * qy)

	return [
		m00, m10, m20, 0.0,
		m01, m11, m21, 0.0,
		m02, m12, m22, 0.0,
		0.0, 0.0, 0.0, 1.0,
	]


def _smooth_quat(prev, curr, smoothing):
	prev = _normalize_quat(prev)
	curr = _normalize_quat(curr)
	dot = prev[0] * curr[0] + prev[1] * curr[1] + prev[2] * curr[2] + prev[3] * curr[3]
	if dot < 0.0:
		curr = (-curr[0], -curr[1], -curr[2], -curr[3])
	qw = (1.0 - smoothing) * prev[0] + smoothing * curr[0]
	qx = (1.0 - smoothing) * prev[1] + smoothing * curr[1]
	qy = (1.0 - smoothing) * prev[2] + smoothing * curr[2]
	qz = (1.0 - smoothing) * prev[3] + smoothing * curr[3]
	return _normalize_quat((qw, qx, qy, qz))


def run_imu_viewer(queue, fps=60, smoothing=0.1):
	pygame.init()
	display = (900, 600)
	pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
	pygame.display.set_caption("IMU Viewer")

	glEnable(GL_DEPTH_TEST)
	glClearColor(0.05, 0.05, 0.08, 1.0)
	gluPerspective(45, display[0] / display[1], 0.1, 50.0)

	last = (1.0, 0.0, 0.0, 0.0)
	clock = pygame.time.Clock()

	running = True
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False

		latest = None
		while True:
			try:
				latest = queue.get_nowait()
			except Empty:
				break

		if latest is not None:
			qw, qx, qy, qz, _timestamp, _host_time = latest
			last = _smooth_quat(last, (qw, qx, qy, qz), smoothing)

		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		glLoadIdentity()
		glTranslatef(0.0, 0.0, -6.0)

		glMultMatrixf(_quat_to_matrix(last))

		_draw_axes()
		_draw_cube()
		pygame.display.flip()
		clock.tick(fps)

	pygame.quit()


if __name__ == "__main__":
	from queue import Queue
	from python_host.serial.serial_reader import SerialReader

	q = Queue(maxsize=256)
	reader = SerialReader(q, print_raw=False)
	reader.start()
	run_imu_viewer(q)

