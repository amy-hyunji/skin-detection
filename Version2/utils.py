def get_param(tar, src):
	diff = 0
	compare = 0
	lower = True

	for i in range(3):
		_diff = float(tar[i]) - float(src[i])
		compare += _diff
		diff += abs(_diff)

	if (diff <= 100): param = 0.0
	elif (diff >= 300): param = 0.2
	else: param = (diff - 100) / 200 * 0.2

	if (compare < 0): lower = True
	else: lower = False

	return param, lower
