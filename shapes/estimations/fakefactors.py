import logging
import ROOT
from .defaults import _name_string, _process_map, _dataset_map
logger = logging.getLogger("")


def fake_factor_estimation(
    rootfile,
    channel,
    selection,
    variable,
    variation="Nominal",
    is_embedding=True,
    sub_scale=1.0,
    special="",
    doTauES=False,
):
    if is_embedding:
        if doTauES:
            procs_to_subtract = [special, "ZL", "TTL", "VVL"]
        else:
            procs_to_subtract = ["EMB", "ZL", "TTL", "VVL"]
    else:
        procs_to_subtract = ["ZTT", "ZL", "TTT", "TTL", "VVT", "VVL"]
    if special == "TauES":
        logger.debug("TauES special selection")
    logger.debug(
        "Trying to get object {}".format(
            _name_string.format(
                dataset="data",
                channel=channel,
                process="",
                selection="-" + selection if selection != "" else "",
                variation="anti_iso"
                if "scale_t" in variation or "sub_syst" in variation
                else variation,
                variable=variable,
            )
        )
    )
    base_hist = rootfile.Get(
        _name_string.format(
            dataset="data",
            channel=channel,
            process="",
            selection="-" + selection if selection != "" else "",
            variation="anti_iso"
            if "scale_t" in variation or "sub_syst" in variation
            else variation,
            variable=variable,
        )
    ).Clone()
    for proc in procs_to_subtract:
        if "anti_iso_CMS_scale_t_emb" in variation and proc != "EMB":
            logger.debug(
                "Trying to get object {}".format(
                    _name_string.format(
                        dataset=_dataset_map[proc],
                        channel=channel,
                        process="-" + _process_map[proc],
                        selection="-" + selection if selection != "" else "",
                        variation=variation.replace("anti_iso_CMS_scale_t_emb","anti_iso_CMS_scale_t") if not "sub_syst" in variation else "anti_iso",
                        variable=variable,
                    )
                )
            )
            base_hist.Add(
                rootfile.Get(
                    _name_string.format(
                        dataset=_dataset_map[proc],
                        channel=channel,
                        process="-" + _process_map[proc],
                        selection="-" + selection if selection != "" else "",
                        variation=variation.replace("anti_iso_CMS_scale_t_emb","anti_iso_CMS_scale_t") if not "sub_syst" in variation else "anti_iso",
                        variable=variable,
                    )
                ),
                -sub_scale,
            )
        else:
            logger.debug(
                "Trying to get object {}".format(
                    _name_string.format(
                        dataset=_dataset_map[proc],
                        channel=channel,
                        process="-" + _process_map[proc],
                        selection="-" + selection if selection != "" else "",
                        variation=variation if not "sub_syst" in variation else "anti_iso",
                        variable=variable,
                    )
                )
            )
            base_hist.Add(
                rootfile.Get(
                    _name_string.format(
                        dataset=_dataset_map[proc],
                        channel=channel,
                        process="-" + _process_map[proc],
                        selection="-" + selection if selection != "" else "",
                        variation=variation if not "sub_syst" in variation else "anti_iso",
                        variable=variable,
                    )
                ),
                -sub_scale,
            )
    proc_name = "jetFakes" if is_embedding else "jetFakesMC"
    if doTauES:
        proc_name = "jetFakes{}".format(special)
    if variation in ["anti_iso"]:
        ff_variation = "Nominal"
    else:
        ff_variation = variation.replace("anti_iso_", "")
    variation_name = (
        base_hist.GetName()
        .replace("data", proc_name)
        .replace(
            variation
            if "scale_t" not in variation and "sub_syst" not in variation
            else "anti_iso",
            ff_variation,
        )
        .replace("#" + channel, "#" + "-".join([channel, proc_name]), 1)
    )
    base_hist.SetName(variation_name)
    base_hist.SetTitle(variation_name)
    logger.debug("Finished estimation of shape %s.", variation_name)
    return base_hist