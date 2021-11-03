import unittest
from tisane.data import Dataset, DataVector
from typing import Any, List
import typing  # for typing.Unit
import re


# for decorating class methods and extending docstrings
# from: https://stackoverflow.com/questions/60000179/sphinx-insert-argument-documentation-from-parent-method/60012943#60012943
class extend_docstring:
    def __init__(self, method, replace=None, replaceWith=None):
        self.doc = method.__doc__
        if replace and replaceWith:
            self.doc = re.sub(replace, replaceWith, self.doc)

    def __call__(self, function):
        if self.doc is not None:
            doc = function.__doc__
            function.__doc__ = self.doc
            if doc is not None:
                function.__doc__ += doc
        return function

def splitTable(mystr: str):
    assert (
        mystr.count("</tbody></table>") > 0
    ), 'Expected to find "</tbody></table>" in {}'.format(mystr)

    index = mystr.find("</tbody></table>")
    assert index > -1

    firstPart = mystr[:index]
    secondPart = mystr[index:]
    return firstPart, secondPart


class AbstractVariable:
    """Super class for all variables, containing basic common attributes.

    Parameters
    ----------
    name : str
        The name of the variable. If you have data, this should correspond to
        the column's name. The dataset must be in long format.
    data : DataVector, optional
        For internal use only.

    Attributes
    ----------
    relationships : list of Has, Repeats, Nests, Associates, or Moderates
        The relationships this variable has with other variables
    name : str
        The name of the variable. If you are going to use data, this should correspond to the column's name.
    data : DataVector
        The data for this variable, in long format.

    """

    name: str
    data: DataVector
    relationships: List[typing.Union["Has", "Repeats", "Nests"]]

    def __init__(self, name: str, data: None):
        self.name = name
        self.data = data  # or replace with DataVector()?
        self.relationships = list()

    def add_data(self, data):
        self.data = data

    # @param effect the variable causes
    def causes(self, effect: "AbstractVariable"):
        """Adds a `causes` relationship to a data variable.

        Parameters
        ----------
        effect : AbstractVariable
            The effect of the data variable

        See Also
        --------
        associates_with: create a correlation relationship

        Examples
        --------

        >>> import tisane as ts
        >>> adult = ts.Unit(name="adult")
        >>> pounds_lost = adult.numeric("pounds_lost")
        >>> group = ts.Unit(name="group")
        >>> exercise_regimen = group.nominal(name="exercise_regimen")
        >>> exercise_regimen.causes(pounds_lost) # the exercise regimen causes the number of pounds lost

        """
        # Update both variables
        cause_relat = Causes(cause=self, effect=effect)
        self.relationships.append(cause_relat)
        effect.relationships.append(cause_relat)

    # @param variable associated with self
    def associates_with(self, variable: "AbstractVariable"):
        """ Adds a correlation relationship to a data variable.

        Parameters
        ----------
        variable : "AbstractVariable"
            The variable that this variable is associated with/correlated to.

        See Also
        --------
        causes: add a causal relationship

        Examples
        --------

        >>> import tisane as ts
        >>> adult = ts.Unit(name="adult", cardinality=386)
        >>> pounds_lost = adult.numeric(name="pounds_lost")
        >>> age = adult.numeric(name="age")
        >>> age.associates_with(pounds_lost)

        """
        # Update both variables
        assoc_relat = Associates(lhs=self, rhs=variable)
        self.relationships.append(assoc_relat)
        variable.relationships.append(assoc_relat)

    # @param moderator contains variables that moderates the effect of self on @param on variable
    def moderates(
        self,
        moderator: typing.Union["AbstractVariable", List["AbstractVariable"]],
        on: "AbstractVariable",
    ):
        """Adds an interaction relationship to a data variable

        Parameters
        ----------
        moderator : AbstractVariable or List[AbstractVariable]
            The variable(s) that moderate(s) the effect of this variable on another variable
        on : AbstractVariable
            The target of the moderated effect

        Examples
        --------

        Race interacts with SES to cause math achievement:

        >>> import tisane as ts
        >>> student = ts.Unit(name="student_id")
        >>> race = student.nominal(name="race")
        >>> ses = student.ordinal(name="SES")
        >>> math_achievement = student.numeric(name="math_score")
        >>> race.moderates(moderator=ses, on=math_achievement)

        """
        # Update both variables
        m_vars = list()
        m_vars.append(self)
        if isinstance(moderator, AbstractVariable):
            m_vars.append(moderator)  # Add moderator to vars list
        else:
            assert isinstance(moderator, List)
            for m in moderator:
                assert isinstance(m, AbstractVariable)
            m_vars += moderator  # Add moderator to vars list

        moderate_relat = Moderates(moderator=m_vars, on=on)
        self.relationships.append(moderate_relat)

        # Add relationship to moderators
        for v in m_vars:
            if self != v:  # Already added to self
                v.relationships.append(moderate_relat)

        # Add relationship to @param on
        on.relationships.append(moderate_relat)

    def _repr_html_(self):
        rowFormat = """<tr><th scope="row" style="text-align:left">{}</th><td style="text-align:left">{}</td></tr>"""

        tableBody = """<table style="text-align:left"><tbody>{}</tbody></table>"""
        nameRow = rowFormat.format("Name", self.name)
        typeRow = rowFormat.format(
            "Type",
            "<code>{}</code>".format(
                re.sub(r"^[^']*'([^']+)'[^']*$", r"\1", str(type(self)))
            ),
        )
        dataRow = """<tr><th scope="row" style="text-align:left">Data</th><td style="text-align:left">{}</td></tr>""".format(
            self.data if self.data else "No data available"
        )
        return tableBody.format(nameRow + typeRow + dataRow)




class SetUp(AbstractVariable):
    """Class for experiment's environment settings and variables

    This can represent time, year, etc.

    Parameters
    ----------
    name : str
        The name of the variable. If you have data, this should correspond to
        the column's name. The dataset must be in long format.
    order : List, optional
        Use a specific ordering of the values of environment settings.
    cardinality : int, optional
        The number of unique values of the variable.
    data : DataVector, optional
        For internal use only.
    **kwargs : optional
        Additional keyword arguments are not currently implemented, i.e., specifying additional keyword arguments will do nothing.

    Attributes
    ----------
    variable : Measure
        The internal representation of this variable.

    Examples
    --------

    Time as a `SetUp` variable:

    >>> import tisane as ts
    >>> time = ts.SetUp("time")

    Year as a `SetUp` variable, and we know that we have 30 years of data.

    >>> year = ts.SetUp("year", cardinality=30)

    Suppose we had a sensor in the field somewhere, and the sensor records multiple types of data, such as temperature, humidity, etc., as well as the time for each measurement. We can have ``timestamp`` a `SetUp` variable, and we have a temperature for every time stamp.

    >>> sensor = ts.Unit("sensor")
    >>> timestamp = ts.SetUp("timestamp")
    >>> temperature = sensor.numeric("temperature", number_of_instances=timestamp)

    """
    variable: "Measure"

    def __init__(
        self,
        name: str,
        order: List = None,
        cardinality: int = None,
        data=None,
        **kwargs,
    ):
        super(SetUp, self).__init__(name, data)

        # If there is an order of values provided
        if order is not None:
            if cardinality is not None:
                self.variable = Ordinal(
                    name, order=order, cardinality=cardinality, data=data
                )
            else:
                self.variable = Ordinal(name, order=order, data=data)
        else:
            if cardinality is not None:
                self.variable = Nominal(name, data=data, cardinality=cardinality)
            else:
                self.variable = Numeric(name, data)

    def _repr_html_(self):
        superHtml = super(SetUp, self)._repr_html_()
        tableBegin, tableEnd = splitTable(superHtml)

        rowFormat = """<tr><th scope="row" style="text-align:left">{}</th><td style="text-align:left">{}</td></tr>"""
        cardinality = self.get_cardinality()
        cardinalityRow = (
            rowFormat.format("Cardinality", cardinality) if cardinality else ""
        )
        order = (
            self.variable.ordered_cat if isinstance(self.variable, Ordinal) else None
        )
        orderRow = rowFormat.format("Order", ", ".join(order)) if order else ""
        return tableBegin + cardinalityRow + orderRow + tableEnd

    def get_cardinality(self):
        return self.variable.get_cardinality()

    # Estimate the cardinality of a variable by counting the number of unique values in the column of data representing this variable
    def calculate_cardinality_from_data(self, data: Dataset):
        assert data is not None
        data = data.dataset[self.name]  # Get data corresponding to this variable
        unique_values = data.unique()

        return len(unique_values)

    # Assign cardinalty from data
    def assign_cardinality_from_data(self, data: Dataset):
        assert data is not None
        self.cardinality = self.calculate_cardinality_from_data(data)





class Unit(AbstractVariable):
    """Class for Units

    A data variable that can have attributes. For example, if you have people
    in your dataset, and each person has an eye color, height, age, etc., then
    you should make the person variable a `Unit`.

    In statistics, a `Unit` can represent either an `observational
    or experimental unit <https://en.wikipedia.org/wiki/Statistical_unit>`_.

    Parameters
    ----------
    name : str
        The name of the variable. If you have data, this should correspond to
        the column's name. The dataset must be in long format.
    data : DataVector, optional
        For internal use only.
    cardinality : int, optional
        The number of unique values of the variable.
        `cardinality` is optional only if you have a data set.
        If specified, Tisane will check that the cardinality is correct if you
        include data in the design.
        If left unspecified, and data is available, Tisane will try to calculate
        the cardinality.
    **kwargs : optional
        Additional keyword arguments are not currently implemented.

    Attributes
    ----------
    cardinality: int
        The number of unique values of the variable.

    Examples
    --------

    >>> import tisane as ts
    >>> person = ts.Unit(name="person_id")

    An example with cardinality: there were 40 unique groups.

    >>> group = ts.Unit(name="group_id", cardinality=40)

    """

    def __init__(self, name: str, data=None, cardinality: int = None, **kwargs):
        super(Unit, self).__init__(name, data)
        self.cardinality = cardinality

    def _repr_html_(self):
        superHtml = super(Unit, self)._repr_html_()
        tableBegin, tableEnd = splitTable(superHtml)

        rowFormat = """<tr><th scope="row" style="text-align:left">{}</th><td style="text-align:left">{}</td></tr>"""
        cardinality = self.get_cardinality()
        cardinalityRow = (
            rowFormat.format("Cardinality", cardinality) if cardinality else ""
        )
        return tableBegin + cardinalityRow + tableEnd

    def nominal(
        self,
        name: str,
        data=None,
        cardinality=None,
        number_of_instances: typing.Union[int, AbstractVariable, "AtMost", "Per"] = 1,
        **kwargs,
    ):
        """Creates a categorical data variable that is an attribute of a :py:class:`Unit`

        Parameters
        ----------
        name : str
            the name of the variable. If you have data, this should correspond
            to the column's name.
        data : DataVector, optional
            For internal use only.
        cardinality : int, optional
            The number of unique values that the categorical variable can take.
            This should correspond to the number of "categories." If left
            unspecified, Tisane will infer this from the data.
        number_of_instances : int, AbstractVariable, or tisane.AtMost, default=1
            This should be the number of measurements of an attribute per
            unique instance of the associated :py:class:`Unit`. For example, if
            you asked how someone felt 5 different times, the
        **kwargs : optional
            You can optionally specify the categories using the keyword
            argument ``categories``. This should be a list. If left unspecified,
            Tisane will infer this from the data.

        Returns
        -------
        Nominal
            The categorical data variable defined as an attribute of this
            :py:class:`Unit`

        See Also
        --------
        numeric: create a numeric data variable
        ordinal: create an ordered categorical data variable

        Examples
        --------

        A study asked participants how they felt 5 separate times.

        >>> import tisane as ts
        >>> participant = ts.Unit(name="participant")
        >>> feelings = participant.nominal(name="feeling",
        ...                                categories=["sad", "happy", "angry", "excited"], # optional, specified here as an example
        ...                                number_of_instances=5)

        The study also collected participants' eye color.

        >>> eye_color = participant.nominal(name="eye_color",
                                            categories=["blue", "brown", "green", "hazel", "gray", "black"])

        """
        # Create new measure
        measure = Nominal(name, data=data, cardinality=cardinality, **kwargs)
        # Add relationship to self and to measure
        self._has(measure=measure, number_of_instances=number_of_instances)
        # Return handle to measure
        return measure

    def ordinal(
        self,
        name: str,
        order: list,
        cardinality: int = None,
        data=None,
        number_of_instances: typing.Union[int, AbstractVariable, "AtMost", "Per"] = 1,
    ):
        """Creates a categorical data variable whose categories are ordered.

        Parameters
        ----------
        name : str
            the name of the variable. If you have data, this should correspond
            to the column's name.
        order : list
            a list of the categories, in the order desired
        cardinality : int, optional
            The number of unique values that the variable can take. If left
            unspecified, Tisane will automatically infer this from the data,
            if any, or the `order` argument. `cardinality` is required if using
            Tisane without providing data.
        data : DataVector, optional
            For internal use only.
        number_of_instances : int, AbstractVariable, or AtMost, default=1
             This should be the number of measurements of an attribute per
             unique instance of the associated tisane.Unit. For example, if you
             measure the reaction time of a person 10 times, then you should
             enter 10.

        Returns
        -------
        Ordinal
            The categorical data variable with ordered categories

        See Also
        --------
        numeric: create a numeric data variable
        nominal: create an (unordered) categorical variable

        Examples
        --------

        Representing age ranges: <18, 18-30, 31-45, 46-64, 65+

        >>> person = ts.Unit("person")
        >>> ageRange = person.ordinal(name="age", order=["<18", "18-30", "31-45", "46-64", "65+"])

        Representing 3 different treatments of differing amounts of vitamin E:

        >>> pig = ts.Unit("Pig", cardinality=72)  # 72 pigs
        >>> vitamin_e = pig.ordinal("Evit",
        ...                         order=["Evit000", "Evit100", "Evit200"],
        ...                         number_of_instances=1)

        Suppose you have 100 people, and you measure using a Likert scale how
        well they're feeling 10 times, for each person.

        >>> person = ts.Unit("person", cardinality=100) # 100 people
        >>> feeling = person.ordinal("well",
        ...                          order=[1, 2, 3, 4, 5],
        ...                          number_of_instances=10)

        """
        # Create new measure
        measure = Ordinal(name=name, order=order, cardinality=cardinality, data=data)
        # Add relationship to self and to measure
        self._has(measure=measure, number_of_instances=number_of_instances)
        # Return handle to measure
        return measure

    def numeric(
        self,
        name: str,
        data=None,
        number_of_instances: typing.Union[int, AbstractVariable, "AtMost", "Per"] = 1,
    ):
        """Creates a variable that takes on integer or real number values



        Parameters
        ----------
        name : str
            The name of the variable. If you have data, this should correspond to the column's name.
        data : DataVector, optional
            For internal use only.
        number_of_instances : int, AbstractVariable, or tisane.AtMost, default=1
            This should be the number of measurements of an attribute per unique instance of the associated `Unit`. For example, if you measure the reaction time of each person in a study 10 times, then you should enter 10.

        Examples
        --------

        Participants in a study each had their reaction time measured 10 times.

        >>> import tisane as ts
        >>> participant = ts.Unit(name="participant")
        >>> reaction_time = participant.numeric(name="reaction_time",
        ...                                     number_of_instances=10)

        """
        # Create new measure
        measure = Numeric(name=name, data=data)
        # Add relationship to self and to measure
        self._has(measure=measure, number_of_instances=number_of_instances)
        # Return handle to measure
        return measure

    def _has(
        self,
        measure: AbstractVariable,
        number_of_instances: typing.Union[int, AbstractVariable, "AtMost", "Per"],
    ):
        # Figure out the number of times/repetitions this Unit (self) has of the measure

        repet = None
        according_to = None
        if isinstance(number_of_instances, int):
            repet = Exactly(number_of_instances)
        elif isinstance(number_of_instances, AbstractVariable):
            # repet = Exactly(number_of_instances.get_cardinality())
            repet = Exactly(1)
            repet = repet.per(cardinality=number_of_instances)
            according_to = number_of_instances

            # TODO: Add implied relationship of associates with for measures that have number_of_instances as AbstractVariable
        elif isinstance(number_of_instances, AtMost):
            repet = number_of_instances

        elif isinstance(number_of_instances, Per):
            repet = number_of_instances

        # Bind measure and unit to each other
        has_relat = Has(
            variable=self, measure=measure, repetitions=repet, according_to=according_to
        )
        self.relationships.append(has_relat)
        measure.relationships.append(has_relat)

        # Add relationships between @number_of_instances (if AbstractVariable) variables and DV?

    # def repeats(self, measure: "Measure", according_to: "Measure"):
    #     repeats_relat = Repeats(unit=self, measure=measure, according_to=according_to)

    #     self.relationships.append(repeats_relat)
    #     measure.relationships.append(repeats_relat) # is this necessary?

    def nests_within(self, group: "Unit"):
        nest_relat = Nests(base=self, group=group)

        self.relationships.append(nest_relat)
        group.relationships.append(nest_relat)

    def get_cardinality(self):
        return self.cardinality

    # Estimate the cardinality of a variable by counting the number of unique values in the column of data representing this variable
    def calculate_cardinality_from_data(self, data: Dataset):
        assert data is not None
        data = data.dataset[self.name]  # Get data corresponding to this variable
        unique_values = data.unique()

        return len(unique_values)

    # Assign cardinalty from data
    def assign_cardinality_from_data(self, data: Dataset):
        assert data is not None
        self.cardinality = self.calculate_cardinality_from_data(data)


class Measure(AbstractVariable):
    """
    Super class for Measures
    """
    def __init__(self, name: str, data: None, **kwargs):
        super(Measure, self).__init__(name, data)

    # # Composition relationship between two measures
    # def has(
    #     self,
    #     measure: AbstractVariable,
    #     number_of_instances: typing.Union[int, AbstractVariable, "AtMost"] = 1,
    # ):
    #     repet = None
    #     according_to = None
    #     if isinstance(number_of_instances, int):
    #         repet = Exactly(number_of_instances)
    #     elif isinstance(number_of_instances, AbstractVariable):
    #         repet = Exactly(number_of_instances.get_cardinality())
    #         according_to = number_of_instances
    #     elif isinstance(number_of_instances, AtMost):
    #         repet = number_of_instances

    #     # Bind measure and unit to each other
    #     has_relat = Has(
    #         variable=self, measure=measure, repetitions=repet, according_to=according_to
    #     )
    #     self.relationships.append(has_relat)
    #     measure.relationships.append(has_relat)

    # @returns the unit this measure is an attribute of
    def get_unit(self) -> Unit:
        for r in self.relationships:
            if isinstance(r, Has):
                if r.measure is self and isinstance(r.variable, Unit):
                    return r.variable

        return None

    # @returns the unit relationship, None otherwise
    def get_unit_relationship(self) -> "Has":
        for r in self.relationships:
            if isinstance(r, Has):
                if r.measure is self and isinstance(r.variable, Unit):
                    return r

        return None

    def get_number_of_instances(self) -> "NumberValue":
        unit_relat = self.get_unit_relationship()

        if unit_relat is not None:
            return unit_relat.repetitions
        # else
        return Exactly(0)



class Nominal(Measure):
    """ Class for nominal (a.k.a. categorical) measures

    Represents a categorical variable. You never
    instantiate this class directly, and instead you should
    create instances via the :py:meth:`tisane.Unit.nominal` method.

    Parameters
    ----------
    name : str
        The name of the categorical variable. If you have data, this should correspond to the column's name in the data.
    data : DataVector, optional
        For internal use only
    **kwargs : optional
        Additional keyword arguments from the :py:meth:`tisane.Unit.nominal` method, such as ``categories`` or ``cardinality``.

    Attributes
    ----------
    categories : type
        Description of attribute `categories`.
    assert_property : type
        Description of attribute `assert_property`.
    cardinality : type
        Description of attribute `cardinality`.
    self with : type
        Description of attribute `self with`.
    self and : type
        Description of attribute `self and`.
    data

    See Also
    --------
    tisane.Unit.nominal: create a categorical variable associated with a :py:class:`tisane.Unit`

    """
    cardinality: int
    categories = list
    isInteraction: bool
    moderators: List[AbstractVariable]

    def __init__(self, name: str, data=None, **kwargs):
        super(Nominal, self).__init__(name=name, data=data)
        self.data = data
        self.categories = None

        if "isInteraction" in kwargs and kwargs["isInteraction"]:
            assert (
                "moderators" in kwargs
            ), "Must also specify the moderating variables for an interaction term: {}".format(
                name
            )

        self.isInteraction = (
            kwargs["isInteraction"] if "isInteraction" in kwargs else False
        )
        self.moderators = kwargs["moderators"] if "moderators" in kwargs else []

        # for time being until incorporate DataVector class and methods
        if "categories" in kwargs.keys():
            self.categories = kwargs["categories"]
            num_categories = len(kwargs["categories"])
            # assert int(kwargs["cardinality"]) == len(kwargs["categories"])
            if num_categories == 1:
                # self.assert_property(prop="cardinality", val="unary")
                pass
            elif num_categories == 2:
                # self.assert_property(prop="cardinality", val="binary")
                pass
            else:
                assert num_categories > 2
                # self.assert_property(prop="cardinality", val="multi")
            self.cardinality = num_categories

        else:
            if "cardinality" in kwargs.keys():
                self.cardinality = kwargs["cardinality"]
            # cardinality is not specified but categories is specified
            elif "categories" in kwargs.keys():
                num_categories = len(kwargs["categories"])
                self.cardinality = num_categories
            # neither cardinality nor categories are specified
            else:
                # There is no data
                self.cardinality = None
                self.categories = None

        # has data
        if self.data is not None:
            num_categories = len(self.data.get_categories())
            if num_categories == 1:
                pass
                # self.assert_property(prop="cardinality", val="unary")
            elif num_categories == 2:
                pass
                # self.assert_property(prop="cardinality", val="binary")
            else:
                assert num_categories > 2
                # self.assert_property(prop="cardinality", val="multi")

        # # Associate self with unit by add variable relationship to self and to unit
        # unit._has(measure=self, exactly=exactly, up_to=up_to)

    def __str__(self):
        description = (
            f"Nominal variable:\n"
            + f"name: {self.name}, cardinality: {self.cardinality}, categories: {self.categories}"
            + f"data: {self.data}"
        )
        return description

    def _repr_html_(self):
        superHtml = super(Ordinal, self)._repr_html_()
        tableBegin, tableEnd = splitTable(superHtml)

        rowFormat = """<tr><th scope="row" style="text-align:left">{}</th><td style="text-align:left">{}</td></tr>"""
        cardinality = self.get_cardinality()
        cardinalityRow = (
            rowFormat.format("Cardinality", cardinality) if cardinality else ""
        )
        categoryRow = (
            rowFormat.format(
                "Categories", ", ".join(map(lambda x: str(x), self.categories))
            )
            if self.categories
            else ""
        )
        return tableBegin + cardinalityRow + categoryRow + tableEnd

    # @returns cardinality
    def get_cardinality(self):
        return self.cardinality

    # @returns categories
    def get_categories(self):
        return self.categories

    # Estimate the cardinality of a variable by counting the number of unique values in the column of data representing this variable
    def calculate_cardinality_from_data(self, data: Dataset):
        assert data is not None
        if self.isInteraction and self.moderators:
            data_cardinality = 1
            for m in self.moderators:
                if not isinstance(m, Numeric):
                    moderatorData = data.dataset[m.name]
                    data_cardinality *= len(moderatorData.unique())
                pass
            return data_cardinality
        data = data.dataset[self.name]  # Get data corresponding to this variable
        unique_values = data.unique()

        return len(unique_values)

    # Get the number of unique categorical values this nominal variable represents
    def calculate_categories_from_data(self, data: Dataset) -> List[Any]:
        assert data is not None

        def getUniqueValuesList(name):
            nameData = data.dataset[name]
            return map(lambda x: str(x), nameData.unique().tolist())

        if self.isInteraction and self.moderators:
            categories = (
                getUniqueValuesList(self.moderators[0].name)
                if not isinstance(self.moderators[0], Numeric)
                else [""]
            )
            if len(self.moderators) > 1:
                for mod in self.moderators[1:]:
                    if not isinstance(mod, Numeric):
                        categories = [
                            "{}.{}".format(cat1, cat2)
                            for cat1 in categories
                            for cat2 in getUniqueValuesList(mod.name)
                        ]
                    pass
            return categories

        data = data.dataset[self.name]  # Get data corresponding to this variable
        unique_values = data.unique()

        return unique_values

    # Assign cardinalty from data
    def assign_cardinality_from_data(self, data: Dataset):
        assert data is not None
        self.cardinality = self.calculate_cardinality_from_data(data)

    # Assign categories from data
    def assign_categories_from_data(self, data: Dataset):
        assert data is not None
        self.categories = self.calculate_categories_from_data(data)



class Ordinal(Measure):
    """Represents ordinal measures

    Represents a categorical variable whose categories are ordered. You never
    instantiate this class directly, and instead you should
    create instances via the :py:meth:`tisane.Unit.ordinal` method.

    Parameters
    ----------
    name : str
        The name of the ordinal variable. If you have data, this should be the column name in the data.
    order : list
        The ordering of the categories of the variable
    cardinality : int, optional
        The number of unique values for the variable. This should
        equal the length of `order`.
    data : DataVector, optional
        For internal use only.


    Attributes
    ----------
    ordered_cat : type
        Description of attribute `ordered_cat`.
    properties : type
        Description of attribute `properties`.
    data : DataVector
        The data associated with this variable
    cardinality : int
        The number of values the ordered categorical variable can take on

    See Also
    --------
    tisane.Unit.ordinal : create an ordinal measure attribute of a given `tisane.Unit`

    """
    cardinality: int
    ordered_cat: list

    def __init__(self, name: str, order: list, cardinality: int = None, data=None):
        super(Ordinal, self).__init__(name=name, data=data)
        self.ordered_cat = order
        self.data = data
        self.properties = dict()
        # self.assert_property(prop="dtype", val="ordinal")

        # Order must be provided
        self.ordered_cat = order
        num_categories = len(self.ordered_cat)
        self.cardinality = num_categories
        if num_categories == 1:
            pass
            # self.assert_property(prop="cardinality", val="unary")
        elif num_categories == 2:
            pass
            # self.assert_property(prop="cardinality", val="binary")
        else:
            assert num_categories > 2
            # self.assert_property(prop="cardinality", val="multi")

        # Verify that order and cardinality match
        if cardinality is not None:
            assert self.cardinality == len(order)
        self.cardinality = len(order)

        # # Associate self with unit by add variable relationship to self and to unit
        # unit._has(measure=self, exactly=exactly, up_to=up_to)

    def __str__(self):
        description = (
            f"Ordinal variable:\n"
            + f"name: {self.name}, cardinality: {self.cardinality}, ordered categories: {self.ordered_cat}"
            + f"data: {self.data}"
        )
        return description

    def _repr_html_(self):
        superHtml = super(Ordinal, self)._repr_html_()
        tableBegin, tableEnd = splitTable(superHtml)

        rowFormat = """<tr><th scope="row" style="text-align:left">{}</th><td style="text-align:left">{}</td></tr>"""
        cardinality = self.get_cardinality()
        cardinalityRow = (
            rowFormat.format("Cardinality", cardinality) if cardinality else ""
        )
        orderRow = (
            rowFormat.format(
                "Order", ", ".join(map(lambda x: str(x), self.ordered_cat))
            )
            if self.ordered_cat
            else ""
        )
        return tableBegin + cardinalityRow + orderRow + tableEnd

    # @returns cardinality
    def get_cardinality(self):
        return self.cardinality

    # @returns categories in their order
    def get_categories(self):
        return self.ordered_cat

    # Estimate the cardinality of a variable by counting the number of unique values in the column of data representing this variable
    def calculate_cardinality_from_data(self, data: Dataset):
        assert data is not None
        data = data.dataset[self.name]  # Get data corresponding to this variable
        unique_values = data.unique()

        return len(unique_values)



class Numeric(Measure):
    """Represents numeric variables

    Numeric variables take on values that are integers, real numbers,
    ratios, etc. You never
    instantiate this class directly, and instead you should
    create instances via the :py:meth:`Unit.numeric` method.

    Parameters
    ----------
    name : str
        The name of the numeric variable. If you have data, this should correspond to the column's name in the data.
    data : DataVector, optional
        For internal use only.

    Attributes
    ----------
    properties : dict
        Description of attribute `properties`.
    data

    See Also
    --------
    tisane.Unit.numeric : create a `Numeric` variable attributed to a given `tisane.Unit`

    """
    def __init__(self, name: str, data=None):
        super(Numeric, self).__init__(name=name, data=data)
        self.data = data
        self.properties = dict()
        # self.assert_property(prop="dtype", val="numeric")

        # # Associate self with unit by add variable relationship to self and to unit
        # unit._has(measure=self, exactly=exactly, up_to=up_to)

    def __str__(self):
        description = f"Numeric variable:\n" + f"name: {self.name}, " + f"data: {self.data}"
        return description

    def get_cardinality(self):
        if self.data is not None:
            # Return number of unique values
            raise NotImplementedError
        else:
            return 1


##### Conceptual relationships
"""
Class for Cause relationships
"""


class Causes(object):
    cause: AbstractVariable
    effect: AbstractVariable

    def __init__(self, cause: AbstractVariable, effect: AbstractVariable):
        self.cause = cause
        self.effect = effect


"""
Class for Associate relationships
"""


class Associates(object):
    lhs: AbstractVariable
    rhs: AbstractVariable

    def __init__(self, lhs: AbstractVariable, rhs: AbstractVariable):
        self.lhs = lhs
        self.rhs = rhs


"""
Class for Moderate relationships (for Interactions)
"""


class Moderates(object):
    moderator: List[AbstractVariable]
    on: AbstractVariable

    def __init__(self, moderator: List[AbstractVariable], on: AbstractVariable):
        self.moderator = moderator
        self.on = on


##### Data measurement relationships
# """
# Class for Has relationships
# """


class Has:
    # TODO: Finish
    """Class for Has relationships

    Parameters
    ----------
    variable : AbstractVariable
        Description of parameter `variable`.
    measure : AbstractVariable
        Description of parameter `measure`.
    repetitions : "NumberValue"
        Description of parameter `repetitions`.
    according_to : AbstractVariable
        Description of parameter `according_to`.
    **kwargs : type
        Description of parameter `**kwargs`.

    Attributes
    ----------
    variable
    measure
    repetitions
    according_to

    """
    variable: AbstractVariable
    measure: AbstractVariable
    repetitions: "NumberValue"
    according_to: AbstractVariable

    def __init__(
        self,
        variable: AbstractVariable,
        measure: AbstractVariable,
        repetitions: "NumberValue",
        according_to: AbstractVariable = None,
        **kwargs,
    ):
        self.variable = variable
        self.measure = measure
        self.repetitions = repetitions
        self.according_to = according_to


class Repeats:
    # TODO: finish
    """Class for expressing repeated measures

    Parameters
    ----------
    unit : Unit
        Description of parameter `unit`.
    measure : Measure
        Description of parameter `measure`.
    according_to : Measure
        Description of parameter `according_to`.

    Attributes
    ----------
    unit
    measure
    according_to

    """
    unit: Unit
    measure: Measure
    according_to: Measure

    def __init__(self, unit: Unit, measure: Measure, according_to: Measure):
        self.unit = unit
        self.measure = measure
        self.according_to = according_to


class Nests:
    # TODO: Finish
    """Class for expressing nesting relationship between units

    Parameters
    ----------
    base : Unit
        Description of parameter `base`.
    group : Unit
        Description of parameter `group`.

    Attributes
    ----------
    base
    group

    """
    base: Unit
    group: Unit

    def __init__(self, base: Unit, group: Unit):
        self.base = base
        self.group = group


class NumberValue:
    # TODO: Finish
    """Wrapper class for expressing values for the number of repetitions of a condition, etc.

    Parameters
    ----------
    value : int
        Description of parameter `value`.

    Attributes
    ----------
    value

    """
    value: int

    def __init__(self, value: int):
        self.value = value

    def is_greater_than_one(self):
        return self.value > 1

    def is_equal_to_one(self):
        return self.value == 1

    def get_value(self):
        return self.value

    def per(self, cardinality: AbstractVariable=None, number_of_instances: AbstractVariable=None):
        """Express a `per` relationship on a given `NumberValue`

        Even though `cardinality` and `number_of_instances` are both
        optional parameters, this method requires exactly one of them to be
        specified -- you currently cannot specify both.

        Parameters
        ----------
        cardinality : AbstractVariable, optional
            The :py:class:`AbstractVariable` whose cardinality we want to use
        number_of_instances : AbstractVariable, optional
            The :py:class:`AbstractVariable` whose number of instances we want
            to use

        Returns
        -------
        tisane.variable.Per
            An object representing a "_ per _" relationship.

        """
        assert number_of_instances or cardinality, "Exactly one of the parameters `number_of_instances` and `cardinality` must be not `None`"
        assert not (number_of_instances and cardinality), "Cannot have both `number_of_instances` and `cardinality` specified as non-`None` values"
        return Per(number=self, cardinality=cardinality, number_of_instances=number_of_instances)






class Exactly(NumberValue):
    """Class for expressing exact values

    Used to represent when the ``number_of_instances`` parameter of a variable
    (such as :py:class:`tisane.Unit`, :py:class:`Numeric`/:py:meth:`tisane.Unit.numeric`, etc.)
    is supposed to be *exactly* :py:attr:`value`

    Parameters
    ----------
    value: int
        the exact value to be used.
    """
    def __init__(self, value: int):
        super(Exactly, self).__init__(value)

    @extend_docstring(NumberValue.per, "`NumberValue`", "`Exactly`")
    def per(self, cardinality: AbstractVariable=None, number_of_instances: AbstractVariable=None):
        """
        See Also
        --------
        tisane.AtMost.per : create a per relationship with an :py:class:`AtMost` multiplier

        Examples
        --------

        Rats are either given a supplement or a placebo three times a day, so exactly 3 *per* day

        >>> import tisane as ts
        >>> from tisane import Exactly
        >>> rat = ts.Unit(name="rat_id", cardinality=30) # 30 rats in the study
        >>> days = rat.ordinal(name="day_num", cardinality=28) # 4 weeks of data for each rat
        >>> memory_test_result = rat.numeric(name="memory_test_result",
        ...                                  number_of_instances=days)
        >>> supplements = rat.nominal(name="supplement",
        ...                           categories=["placebo", "supp"],
        ...                           number_of_instances=Exactly(3).per(cardinality=days))

        """
        return super(Exactly, self).per(cardinality=cardinality, number_of_instances=number_of_instances)


class AtMost(NumberValue):
    """An upper bound of a number of instances

    Used to represent when the number of instances of a
    data variable has a ceiling. Should be given to the
    ``number_of_instances`` parameter of :py:meth:`Unit.nominal`, :py:meth:`Unit.numeric`, or
    :py:meth:`Unit.ordinal`.

    Parameters
    ----------
    value : int or AbstractVariable
        The value of the upper bound. If an :py:class:`tisane.variable.AbstractVariable`, then the cardinality of
        `value` is used as the upper bound.

    Examples
    --------

    A study using MTurkers allowed the MTurkers to participate
    in the study at most 20 times.

    >>> import tisane as ts
    >>> mturker = ts.Unit(name="mturker_id")
    >>> response = mturker.ordinal(name="response", number_of_instances=AtMost(20))

    """

    def __init__(self, value: typing.Union[int, AbstractVariable]):
        if isinstance(value, int):
            super(AtMost, self).__init__(value)
        elif isinstance(value, AbstractVariable):
            super(AtMost, self).__init__(value.get_cardinality())

    @extend_docstring(NumberValue.per, "`NumberValue`", "`AtMost`")
    def per(self, cardinality: AbstractVariable=None, number_of_instances: AbstractVariable=None):
        """
        See Also
        --------
        tisane.Exactly.per : create a per relationship with an exact multiplier

        Examples
        --------

        Suppose we have a within-subjects study where participants are subjected
        to two conditions and can memorize a list of numbers at most five times
        in both conditions, before being tested.

        >>> import tisane as ts
        >>> from tisane import AtMost
        >>> participant = ts.Unit(name="participant")
        >>> condition = participant.nominal(name="condition",
        ...                                 cardinality=2,
        ...                                 number_of_instances=2)
        >>> memorization_session_time = participant.numeric(
        ...                    name="learning_session_time",
        ...                    number_of_instances=AtMost(5).per(
        ...                              number_of_instances=condition))

        >>> import tisane as ts
        >>> variable = ts.Unit(name="variable", cardinality=5)
        >>> atmost_five_per_variable = ts.AtMost(5).per(cardinality=variable)
        >>> atmost_five_per_variable.value # this should be 5 * (cardinality of variable = 5)
        25


        """
        return super(AtMost, self).per(cardinality=cardinality, number_of_instances=number_of_instances)

"""
Class for expressing Per relationships
"""


class Per(NumberValue):
    """ Represents a "per" relationship, such as "2 per participant"

    Enables complex number of instances where the number of instances is
    a multiple of the number of instances or cardinality of another variable.

    Instead of instantiating this class directly, you should use the methods
    :py:meth:`tisane.Exactly.per` or :py:meth:`tisane.AtMost.per`.

    Parameters
    ----------
    number : NumberValue
        A `NumberValue` object that fills in the first blank in "_ per _".
        Should have the type :py:class:`Exactly` or :py:class:`AtMost`
    cardinality : AbstractVariable
        Designates that the blank in "`number` per _" should be filled in with
        the cardinality of the given :py:class:`AbstractVariable`
    number_of_instances : Measure
        Designates that the blank in "`number` per _" should be filled in with
        the number of instances of the given :py:class:`Measure`, such as a
        :py:class:`Nominal`, :py:class:`Numeric`, or :py:class:`Ordinal`.

    Attributes
    ----------
    variable : AbstractVariable
        The data variable use as the
    value : int
        The total value given by the `Per` object. If using cardinality,
        then this is calculated as `number` * (cardinality of `variable`).
        If using number of instances, then this is calculated as
        `number` * (number of instances of `variable`)
    number : NumberValue
        The base multiplier of the `Per` instance, which is used to calculate
        :py:attr:`value`
    cardinality  : bool
        Whether or not this `Per` instance is using the cardinality of
        :py:attr:`variable` to calculate the value.
    number_of_instances : bool
        Whether or not this `Per` instance is using the number of instances of
        :py:attr:`variable`

    """
    number: NumberValue
    variable: AbstractVariable
    cardinality: bool
    number_of_instances: bool
    value: int

    def __init__(
        self,
        number: NumberValue,
        cardinality: AbstractVariable = None,
        number_of_instances: Measure = None,
    ):
        self.number = number
        if number_of_instances is not None:
            assert cardinality is None

            self.variable = number_of_instances
            self.cardinality = False
            self.number_of_instances = True

            # Only measures have number_of_instances
            assert (self.variable, Measure)
            self.value = number.value * self.variable.get_number_of_instances().value

        else:
            assert number_of_instances is None
            assert cardinality is not None

            self.variable = cardinality
            self.cardinality = True
            self.number_of_instances = False

            # if self.variable.get_cardinality() is None:
            #     import pdb; pdb.set_trace()
            self.value = number.value * self.variable.get_cardinality()

        assert(self.cardinality or self.number_of_instances, "Must specify either cardinality or number_of_instances (exclusive or) for Per")
        assert(not self.cardinality if self.number_of_instances else True)
        assert(not self.number_of_instances if self.cardinality else True)
