=====
Usage
=====

Installation
------------

To use ``bse``, first install it using pip:

.. code:: console

   $ pip install bse

Example
-------

.. code-block:: python

   from bse import BSE

   bse = BSE()

   bse.exit() # close requests session

.. code-block:: python
   :caption: Using 'with' statement

   with BSE() as bse:
      pass

API
___

.. autoclass:: bse.BSE

General Methods
---------------

.. automethod:: bse.BSE.exit

.. automethod:: bse.BSE.getScripName

.. automethod:: bse.BSE.getScripCode

Download Reports
----------------
.. automethod:: bse.BSE.bhavcopyReport

.. automethod:: bse.BSE.deliveryReport

Corporate Filings
-----------------

.. automethod:: bse.BSE.announcements

.. automethod:: bse.BSE.actions

.. automethod:: bse.BSE.resultCalendar

Market Updates and Summary
--------------------------

.. automethod:: bse.BSE.gainers

.. automethod:: bse.BSE.losers

.. automethod:: bse.BSE.near52WeekHighLow

.. automethod:: bse.BSE.quote

.. automethod:: bse.BSE.quoteWeeklyHL

.. automethod:: bse.BSE.listSecurities
