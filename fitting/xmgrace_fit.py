from string import Template
from tempfile import NamedTemporaryFile
import subprocess
import re
import argparse

TEMPLATE = """fit formula "y = $formula"
fit with $parameters_num parameters
fit prec 0.01
$parameters
	nonlfit(s0,500)
	copy s0 to s2
	s2.y = $formula
	autoscale
	xaxis  bar linewidth 2.0
	xaxis  label "x"
	xaxis  tick major linewidth 2.0
	xaxis  tick minor linewidth 2.0
	xaxis  label char size 2.000000
	xaxis  ticklabel char size 1.500000
	yaxis  bar linewidth 2.0
	yaxis  label "y"
	yaxis  label char size 2.000000
	yaxis  tick major linewidth 2.0
	yaxis  tick minor linewidth 2.0
	yaxis  ticklabel char size 1.500000
	s0 legend  "data"
	s0 symbol 1
	s0 symbol size 1.000000
	s0 symbol color 1
	s0 symbol pattern 1
	s0 symbol fill color 1
	s0 symbol fill pattern 1
	s0 symbol linewidth 1.0
	s0 symbol linestyle 1
	s0 line type 0
	s1 symbol 1
	s1 symbol size 1.000000
	s1 symbol color 1
	s1 symbol pattern 1
	s1 symbol fill color 1
	s1 symbol fill pattern 0
	s1 symbol linewidth 2.0
	s1 symbol linestyle 1
	s1 line type 0
	s2 legend  "fit"
	s2 symbol 0
	s2 line type 1
	s2 line linestyle 1
	s2 line linewidth 2.0
	s2 line color 2
	s2 line pattern 1
	with g0
	subtitle "fit y = $formula"
	view 0.200000, 0.150000, 1.150000, 0.850000
	print to ""
	hardcopy device "PNG"
	device "PNG" font antialiasing on"""


def generate_xmscript(formula, *parameters):
    """Generate the xmgrace script for fitting

    Args:
        formula (str): formula to fit

    Returns:
        str: xmgrace script
    """
    s = Template(TEMPLATE)

    parameters_list = list()
    for i, p in enumerate(parameters):
        parameters_list.extend([f"a{i} = {p}", f"a{i} constraints off"])
    parameters_str = "\n".join(parameters_list)

    content = s.substitute(formula=formula, parameters_num=len(
        parameters), parameters=parameters_str)
    return content


def wsrc_nlfit(datfile_name, formula, print_output=False, **guesses):
    """Fit the WSRC sensor

    Args:
        datfile_name (str): name of the file containing the data
        formula (str): formula to fit

    Returns:
        dict: fitted parameters
    """
    cmd_wsrc = "xmgrace -block $datfile_name -bxy 1:3 -bxy 1:2 -param $scriptfile_name -hardcopy -noprint"
    return nlfit(datfile_name, formula, cmd=cmd_wsrc, print_output=print_output, **guesses)


def nlfit(datfile_name,
          formula,
          cmd="xmgrace -block $datfile_name -bxy 1:2 -param $scriptfile_name -hardcopy -noprint",
          print_output=False,
          **guesses):
    """ Non-linear fit with xmgrace

    Args:
        datfile_name (str): name of the file containing the data
        formula (str): formula to fit
        cmd (str, optional): command to execute. Defaults to "xmgrace -block $datfile_name -bxy 1:2 -param $scriptfile_name -hardcopy -noprint".  

    Returns:
        dict : fitted parameters
    """

    diff = True

    SEP = " = "
    PATTERNS = [k + SEP for k in guesses.keys()]

    with NamedTemporaryFile(mode="w", delete=False) as tmpfile:
        scriptfile_name = tmpfile.name

    cmd_tmpl = Template(cmd)
    n = 0
    while diff and n < 100:
        n += 1
        xmscript = generate_xmscript(formula, *guesses.values())
        with open(scriptfile_name, mode="w",) as tmpfile:
            tmpfile.write(xmscript)

        cmd_exec = cmd_tmpl.substitute(
            datfile_name=datfile_name, scriptfile_name=scriptfile_name)
        res = subprocess.run(
            cmd_exec, shell=True, executable="/bin/bash", stdout=subprocess.PIPE)
        output = res.stdout.decode("utf-8")
        output_lines = output.splitlines()

        diffs = list()
        for p in PATTERNS:
            # Parsing of output and retrieval last displayed value
            m = [l for l in output_lines if re.search(p, l)]
            val = float(m[-1].split(SEP)[-1])

            key = p.rstrip(SEP)

            diffs.append(guesses[key] != val)

            guesses[key] = val
        diff = all(diffs)
        if print_output:
            print('.', end='')
    if print_output:
        print()
        print(output)
    if n == 100:   
        print("[WARNING] Max iterations reached")
    
    return guesses


if __name__ == '__main__':
    #    parser = argparse.ArgumentParser(prog="wsrc fitting")
    #    parser.add_argument('datfile_name')
    #    args = parser.parse_args()
    #    wsrc_nlfit(args.datfile_name)
    wsrc_nlfit('xmgrace_inputs/wsrc_CISCO.dat',
               "10000*(a0-S1.y)*(a1+a2*x^a3)", a0=1, a1=1, a2=1, a3=1)
