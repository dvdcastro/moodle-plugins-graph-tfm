<?php
// This file is part of the Sertifier Certificate module for Moodle - https://moodle.org/
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
// along with Moodle.  If not, see <https://www.gnu.org/licenses/>.

/**
 * Code fragment to define the version of the certificate module
 *
 * @package    mod_sertifier
 * @copyright  Sertifier <[email]>
 * @license    https://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$plugin->version   = 2021050305;
$plugin->requires  = 2020061500;
$plugin->supported = [39, 405];
$plugin->cron      = 0;
$plugin->component = 'mod_sertifier';
$plugin->maturity  = MATURITY_STABLE;
$plugin->release   = "v1.0.6";
