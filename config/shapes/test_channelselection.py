import sys
import warnings
sys.path.append('../../')

from misc_helper.string_expression_comparison import check_logical_equivalence, check_evaluation_equivalence
from channel_selection import _channel_selection, channel_selection


for channel in ["mt", "et", "tt", "em", "mm", "ee"]:
    for era in ["2016preVFP", "2016postVFP", "2017", "2018"]:
        for special in [None, "TauID", "TauES", "EleES"]:
            for ff_tests in [None]:
                # will raise ValueError since special is not defined in these cases in old channel_selection
                if special == "EleES" and channel != "ee":
                    continue
                if special == "TauID" and channel not in {"mt", "mm"}:
                    continue
                if special == "TauES" and channel not in {"mt"}:
                    continue

                # for cases where i.e. trigger is not defined in old channel_selection for certain eras
                try:
                    tmp1 = _channel_selection(channel, era, special=special, ff_DR=ff_tests).cuts
                except ValueError as e:
                    if str(e) == "Given era does not exist":
                        continue
                    else:
                        raise e

                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    tmp2 = channel_selection(channel, era, special=special, ff_DR=ff_tests).cuts

                assert len(tmp1) == len(tmp2)
                assert [it.name for it in tmp1] == [it.name for it in tmp2]

                for cut1, cut2 in zip(tmp1, tmp2):
                    assert check_logical_equivalence(
                        cut1.expression,
                        cut2.expression,
                        verbose=False,
                    ), "\n".join(
                        [
                            f"Failed for {channel}, {era}, {special}, {ff_tests}",
                            f"Cut1: {cut1.expression}",
                            f"Cut2: {cut2.expression}",
                        ]
                    )
                    assert check_evaluation_equivalence(
                        cut1.expression,
                        cut2.expression,
                        verbose=False,
                    ), "\n".join(
                        [
                            f"Failed for {channel}, {era}, {special}, {ff_tests}",
                            f"Cut1: {cut1.expression}",
                            f"Cut2: {cut2.expression}",
                        ]
                    )

                    print(".", end="")
