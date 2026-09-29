<?php
// This file is part of Moodle - http://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// Moodle is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with Moodle.  If not, see <http://www.gnu.org/licenses/>.

/**
 * Copyright (C) 2014 onwards emeneo (http://www.emeneo.com)
 *
 * @package    blocks
 * @subpackage report_free_seats
 * @copyright  2014 onwards emeneo (http://www.emeneo.com)
 * @author     Flotter Totte ([email])
 */

defined('MOODLE_INTERNAL') || die();

$plugin->version    = 2024091700;
$plugin->requires   = 2010112400;
$plugin->component  = 'block_report_free_seats';
$plugin->cron       = 0;
$plugin->maturity   = MATURITY_STABLE;
$plugin->release    = 'Free seats report version 4.4-a';
