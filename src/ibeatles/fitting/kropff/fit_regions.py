import numpy as np
from lmfit import Model, Parameter
import copy
from qtpy import QtGui
import logging

from src.ibeatles.utilities.status_message_config import (
    StatusMessageStatus,
    show_status_message,
)
import ibeatles.utilities.error as fitting_error
from src.ibeatles.fitting.kropff.get import Get
from src.ibeatles.fitting.kropff.fitting_functions import (
    kropff_high_lambda,
    kropff_bragg_peak_tof,
    kropff_low_lambda,
)
from src.ibeatles.fitting import KropffTabSelected
from src.ibeatles.utilities.array_utilities import find_nearest_index
from src.ibeatles.fitting.kropff.checking_fitting_conditions import (
    CheckingFittingConditions,
)
from src.ibeatles.fitting.kropff import ERROR_TOLERANCE


class FitRegions:
    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent
        self.o_get = Get(parent=parent)
        self.table_dictionary = self.grand_parent.kropff_table_dictionary
        self.progress_bar_ui = self.parent.eventProgress

    def all_regions(self):
        type_error = ""

        # o_event = KropffBraggPeakThresholdCalculator(parent=self.parent,
        #                                              grand_parent=self.grand_parent)
        # o_event.save_all_profiles()

        # o_display = Display(parent=self.parent,
        #                     grand_parent=self.grand_parent)
        # o_display.display_bragg_peak_threshold()

        try:
            self.high_lambda()
            self.low_lambda()
            self.bragg_peak()
        except fitting_error.HighLambdaFittingError as err:
            type_error = err
        except fitting_error.LowLambdaFittingError as err:
            type_error = err
        except fitting_error.BraggPeakFittingError as err:
            type_error = err

        if type_error:
            show_status_message(
                parent=self.parent,
                message=f"Error fitting {type_error}",
                status=StatusMessageStatus.error,
                duration_s=5,
            )

    @staticmethod
    def error_outside_of_tolerance(list_error):
        for _error in list_error:
            if not _error:
                return True

            if _error > ERROR_TOLERANCE:
                return True
        return False

    def high_lambda(self):
        gmodel = Model(kropff_high_lambda, missing="drop", independent_vars=["lda"])

        a0 = self.o_get.a0()
        b0 = self.o_get.b0()

        table_dictionary = self.table_dictionary
        # common_xaxis = None
        nearest_index = -1

        self.progress_bar_ui.setMaximum(len(table_dictionary.keys()))
        self.progress_bar_ui.setVisible(True)
        QtGui.QGuiApplication.processEvents()

        xaxis_common = table_dictionary["0"]["xaxis"]

        for _index, _key in enumerate(table_dictionary.keys()):
            self.progress_bar_ui.setValue(_index + 1)
            QtGui.QGuiApplication.processEvents()

            # if row is locked, continue
            if table_dictionary[_key]["lock"]:
                continue

            right = table_dictionary[_key]["bragg peak threshold"]["right"]

            nearest_index = find_nearest_index(xaxis_common, right)
            xaxis = xaxis_common[nearest_index:-1]
            if len(xaxis) == 0:
                table_dictionary[_key]["rejected"] = True
                continue

            yaxis = table_dictionary[_key]["yaxis"]
            yaxis = yaxis[nearest_index:-1]
            yaxis = -np.log(yaxis)

            try:
                _result = gmodel.fit(yaxis, lda=xaxis, a0=a0, b0=b0)
            except ValueError:
                table_dictionary[_key]["rejected"] = True
                continue
            except TypeError:
                table_dictionary[_key]["rejected"] = True
                continue

            a0_value = _result.params["a0"].value
            a0_error = _result.params["a0"].stderr
            b0_value = _result.params["b0"].value
            b0_error = _result.params["b0"].stderr

            if FitRegions.error_outside_of_tolerance([a0_error, b0_error]):
                table_dictionary[_key]["rejected"] = True
                continue

            yaxis_fitted = kropff_high_lambda(xaxis, a0_value, b0_value)

            table_dictionary[_key]["a0"] = {"val": a0_value, "err": a0_error}
            table_dictionary[_key]["b0"] = {"val": b0_value, "err": b0_error}
            table_dictionary[_key]["fitted"][KropffTabSelected.high_tof] = {
                "xaxis": xaxis,
                "yaxis": yaxis_fitted,
            }

        self.progress_bar_ui.setVisible(False)
        QtGui.QGuiApplication.processEvents()

    def low_lambda(self):
        gmodel = Model(kropff_low_lambda, missing="drop", independent_vars=["lda"])

        ahkl = self.o_get.ahkl()
        bhkl = self.o_get.bhkl()

        table_dictionary = self.table_dictionary

        self.progress_bar_ui.setMaximum(len(table_dictionary.keys()))
        self.progress_bar_ui.setVisible(True)
        QtGui.QGuiApplication.processEvents()

        common_xaxis = None
        nearest_index = -1
        for _index, _key in enumerate(table_dictionary.keys()):
            self.progress_bar_ui.setValue(_index + 1)
            QtGui.QGuiApplication.processEvents()

            # if row is locked, continue
            if table_dictionary[_key]["lock"]:
                continue

            if table_dictionary[_key]["rejected"]:
                continue

            table_entry = table_dictionary[_key]

            if nearest_index == -1:
                xaxis = table_entry["xaxis"]

                left = table_entry["bragg peak threshold"]["left"]

                nearest_index = find_nearest_index(xaxis, left)
                xaxis = xaxis[: nearest_index + 1]
                common_xaxis = xaxis

            a0 = table_entry["a0"]["val"]
            b0 = table_entry["b0"]["val"]

            yaxis = table_entry["yaxis"]
            yaxis = yaxis[: nearest_index + 1]
            yaxis = -np.log(yaxis)

            try:
                _result = gmodel.fit(
                    yaxis,
                    lda=common_xaxis,
                    a0=Parameter("a0", value=a0, vary=False),
                    b0=Parameter("b0", value=b0, vary=False),
                    ahkl=ahkl,
                    bhkl=bhkl,
                )
            except ValueError:
                table_dictionary[_key]["rejected"] = True
                continue

            ahkl_value = _result.params["ahkl"].value
            ahkl_error = _result.params["ahkl"].stderr
            bhkl_value = _result.params["bhkl"].value
            bhkl_error = _result.params["bhkl"].stderr
            yaxis_fitted = kropff_low_lambda(
                common_xaxis, a0, b0, ahkl_value, bhkl_value
            )

            table_dictionary[_key]["ahkl"] = {"val": ahkl_value, "err": ahkl_error}
            table_dictionary[_key]["bhkl"] = {"val": bhkl_value, "err": bhkl_error}
            table_dictionary[_key]["fitted"][KropffTabSelected.low_tof] = {
                "xaxis": common_xaxis,
                "yaxis": yaxis_fitted,
            }

        self.progress_bar_ui.setVisible(False)
        self.grand_parent.kropff_table_dictionary = self.table_dictionary
        QtGui.QGuiApplication.processEvents()

    def bragg_peak(self):
        self.bragg_peak_range()

        # if self.parent.kropff_lambda_settings['state'] == 'fix':
        #     self.bragg_peak_fix_lambda()
        # else:
        #     self.bragg_peak_range_lambda()

    def bragg_peak_range(self):
        """will fit using either fix or range values of lambda_hkl, tau and sigma"""
        logging.info("Fitting bragg peak with:")

        o_get = Get(parent=self.parent)
        list_lambda_hkl = o_get.list_lambda_hkl_initial_guess()
        list_tau = o_get.list_tau_initial_guess()
        list_sigma = o_get.list_sigma_initial_guess()
        logging.info(f"-> {list_lambda_hkl =}")
        logging.info(f"-> {list_tau =}")
        logging.info(f"-> {list_sigma =}")

        # define fitting model
        gmodel = Model(
            kropff_bragg_peak_tof, nan_policy="propagate", independent_vars=["lda"]
        )

        table_dictionary = self.table_dictionary
        fit_conditions = self.parent.kropff_bragg_peak_good_fit_conditions
        o_checking = CheckingFittingConditions(fit_conditions=fit_conditions)

        self.parent.eventProgress.setMaximum(len(table_dictionary.keys()))
        self.parent.eventProgress.setValue(0)
        self.parent.eventProgress.setVisible(True)
        QtGui.QGuiApplication.processEvents()

        for _index, _key in enumerate(table_dictionary.keys()):
            # if row is locked, continue
            if table_dictionary[_key]["lock"]:
                self.parent.eventProgress.setValue(_index)
                QtGui.QGuiApplication.processEvents()
                continue

            if table_dictionary[_key]["rejected"]:
                self.parent.eventProgress.setValue(_index)
                QtGui.QGuiApplication.processEvents()
                continue

            table_entry = table_dictionary[_key]

            xaxis = copy.deepcopy(table_entry["xaxis"])

            a0 = table_entry["a0"]["val"]
            b0 = table_entry["b0"]["val"]
            ahkl = table_entry["ahkl"]["val"]
            bhkl = table_entry["bhkl"]["val"]

            yaxis = copy.deepcopy(table_entry["yaxis"])
            yaxis = -np.log(yaxis)

            is_fitting_ok = False
            for _lambda_hkl in list_lambda_hkl:
                for _sigma in list_sigma:
                    for _tau in list_tau:
                        _result = gmodel.fit(
                            yaxis,
                            lda=xaxis,
                            a0=Parameter("a0", value=a0, vary=False),
                            b0=Parameter("b0", value=b0, vary=False),
                            ahkl=Parameter("ahkl", value=ahkl, vary=False),
                            bhkl=Parameter("bhkl", value=bhkl, vary=False),
                            ldahkl=_lambda_hkl,
                            sigma=_sigma,
                            tau=_tau,
                        )

                        ldahkl_error = _result.params["ldahkl"].stderr
                        sigma_error = _result.params["sigma"].stderr
                        tau_error = _result.params["tau"].stderr
                        ldahkl_value = _result.params["ldahkl"].value
                        sigma_value = _result.params["sigma"].value
                        tau_value = _result.params["tau"].value
                        yaxis_fitted = kropff_bragg_peak_tof(
                            xaxis,
                            a0,
                            b0,
                            ahkl,
                            bhkl,
                            ldahkl_value,
                            sigma_value,
                            tau_value,
                        )

                        is_fitting_ok = o_checking.is_fitting_ok(
                            l_hkl_error=ldahkl_error,
                            t_error=tau_error,
                            sigma_error=sigma_error,
                        )
                        self.parent.eventProgress.setValue(_index)
                        QtGui.QGuiApplication.processEvents()

                        table_dictionary[_key]["lambda_hkl"] = {
                            "val": ldahkl_value,
                            "err": ldahkl_error,
                        }
                        table_dictionary[_key]["tau"] = {
                            "val": tau_value,
                            "err": tau_error,
                        }
                        table_dictionary[_key]["sigma"] = {
                            "val": sigma_value,
                            "err": sigma_error,
                        }
                        table_dictionary[_key]["fitted"][
                            KropffTabSelected.bragg_peak
                        ] = {"xaxis": xaxis, "yaxis": yaxis_fitted}

                        if is_fitting_ok:
                            break

                    if is_fitting_ok:
                        break

                if is_fitting_ok:
                    table_dictionary[_key]["lock"] = True
                    break

        self.parent.eventProgress.setVisible(False)

    def bragg_peak_range_lambda(self):
        """we need to try to fit until the fit worked or we exhausted the full range defined"""
        logging.info("Fitting bragg peak with a range of lambda_hkl:")
        gmodel = Model(
            kropff_bragg_peak_tof, nan_policy="propagate", independent_vars=["lda"]
        )

        # lambda_hkl = self.o_get.lambda_hkl()
        tau = self.o_get.tau()
        sigma = self.o_get.sigma()

        table_dictionary = self.table_dictionary
        fit_conditions = self.parent.kropff_bragg_peak_good_fit_conditions
        o_checking = CheckingFittingConditions(fit_conditions=fit_conditions)

        lambda_hkl_range = np.arange(
            self.parent.kropff_lambda_settings["range"][0],
            self.parent.kropff_lambda_settings["range"][1],
            self.parent.kropff_lambda_settings["range"][2],
        )
        logging.info(f"-> lambda_hkl_range: {lambda_hkl_range}")

        self.parent.eventProgress.setMaximum(len(table_dictionary.keys()))
        self.parent.eventProgress.setValue(0)
        self.parent.eventProgress.setVisible(True)
        QtGui.QGuiApplication.processEvents()

        for _index, _key in enumerate(table_dictionary.keys()):
            # if row is locked, continue
            if table_dictionary[_key]["lock"]:
                self.parent.eventProgress.setValue(_index)
                QtGui.QGuiApplication.processEvents()
                continue

            if table_dictionary[_key]["rejected"]:
                self.parent.eventProgress.setValue(_index)
                QtGui.QGuiApplication.processEvents()
                continue

            table_entry = table_dictionary[_key]

            xaxis = copy.deepcopy(table_entry["xaxis"])

            a0 = table_entry["a0"]["val"]
            b0 = table_entry["b0"]["val"]
            ahkl = table_entry["ahkl"]["val"]
            bhkl = table_entry["bhkl"]["val"]

            yaxis = copy.deepcopy(table_entry["yaxis"])
            yaxis = -np.log(yaxis)

            for _lambda_hkl in lambda_hkl_range:
                _result = gmodel.fit(
                    yaxis,
                    lda=xaxis,
                    a0=Parameter("a0", value=a0, vary=False),
                    b0=Parameter("b0", value=b0, vary=False),
                    ahkl=Parameter("ahkl", value=ahkl, vary=False),
                    bhkl=Parameter("bhkl", value=bhkl, vary=False),
                    ldahkl=_lambda_hkl,
                    sigma=sigma,
                    tau=tau,
                )

                ldahkl_error = _result.params["ldahkl"].stderr
                sigma_error = _result.params["sigma"].stderr
                tau_error = _result.params["tau"].stderr
                ldahkl_value = _result.params["ldahkl"].value
                sigma_value = _result.params["sigma"].value
                tau_value = _result.params["tau"].value
                yaxis_fitted = kropff_bragg_peak_tof(
                    xaxis, a0, b0, ahkl, bhkl, ldahkl_value, sigma_value, tau_value
                )

                if o_checking.is_fitting_ok(
                    l_hkl_error=ldahkl_error, t_error=tau_error, sigma_error=sigma_error
                ):
                    break

            self.parent.eventProgress.setValue(_index)
            QtGui.QGuiApplication.processEvents()

            table_dictionary[_key]["lambda_hkl"] = {
                "val": ldahkl_value,
                "err": ldahkl_error,
            }
            table_dictionary[_key]["tau"] = {"val": tau_value, "err": tau_error}
            table_dictionary[_key]["sigma"] = {"val": sigma_value, "err": sigma_error}
            table_dictionary[_key]["fitted"][KropffTabSelected.bragg_peak] = {
                "xaxis": xaxis,
                "yaxis": yaxis_fitted,
            }
        self.parent.eventProgress.setVisible(False)

    def bragg_peak_fix_lambda(self):
        logging.info("Fitting bragg peak with a fixed initial lambda_hkl:")

        gmodel = Model(
            kropff_bragg_peak_tof, nan_policy="propagate", independent_vars=["lda"]
        )

        lambda_hkl = self.o_get.lambda_hkl()
        logging.info(f"-> lambda_hkl: {lambda_hkl}")
        tau = self.o_get.tau()
        sigma = self.o_get.sigma()

        table_dictionary = self.table_dictionary

        self.progress_bar_ui.setMaximum(len(table_dictionary.keys()))
        self.progress_bar_ui.setVisible(True)
        QtGui.QGuiApplication.processEvents()

        list_key_locked = []
        for _index, _key in enumerate(table_dictionary.keys()):
            self.progress_bar_ui.setValue(_index + 1)
            QtGui.QGuiApplication.processEvents()

            # if row is locked, continue
            if table_dictionary[_key]["lock"]:
                list_key_locked.append(int(_key) + 1)
                continue

            if table_dictionary[_key]["rejected"]:
                continue

            table_entry = table_dictionary[_key]

            xaxis = copy.deepcopy(table_entry["xaxis"])

            a0 = table_entry["a0"]["val"]
            b0 = table_entry["b0"]["val"]
            ahkl = table_entry["ahkl"]["val"]
            bhkl = table_entry["bhkl"]["val"]

            yaxis = copy.deepcopy(table_entry["yaxis"])
            yaxis = -np.log(yaxis)

            _result = gmodel.fit(
                yaxis,
                lda=xaxis,
                a0=Parameter("a0", value=a0, vary=False),
                b0=Parameter("b0", value=b0, vary=False),
                ahkl=Parameter("ahkl", value=ahkl, vary=False),
                bhkl=Parameter("bhkl", value=bhkl, vary=False),
                ldahkl=lambda_hkl,
                sigma=sigma,
                tau=tau,
            )

            if _key in ["2", "3"]:
                logging.info(
                    f"_key: {_key} -> _result.fit_report: {_result.fit_report()}"
                )

            ldahkl_value = _result.params["ldahkl"].value
            ldahkl_error = _result.params["ldahkl"].stderr
            sigma_value = _result.params["sigma"].value
            sigma_error = _result.params["sigma"].stderr
            tau_value = _result.params["tau"].value
            tau_error = _result.params["tau"].stderr
            yaxis_fitted = kropff_bragg_peak_tof(
                xaxis, a0, b0, ahkl, bhkl, ldahkl_value, sigma_value, tau_value
            )

            table_dictionary[_key]["lambda_hkl"] = {
                "val": ldahkl_value,
                "err": ldahkl_error,
            }
            table_dictionary[_key]["tau"] = {"val": tau_value, "err": tau_error}
            table_dictionary[_key]["sigma"] = {"val": sigma_value, "err": sigma_error}
            table_dictionary[_key]["fitted"][KropffTabSelected.bragg_peak] = {
                "xaxis": xaxis,
                "yaxis": yaxis_fitted,
            }

        logging.info(f"-> list of locked keys: {list_key_locked}")

        self.progress_bar_ui.setVisible(False)
        QtGui.QGuiApplication.processEvents()
