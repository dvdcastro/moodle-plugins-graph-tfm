<?php
// This file is part of Moodle - https://moodle.org/
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
 * SRL Advisor local plugin version information.
 *
 * @package    local_srl_advisor
 * @copyright  2026 Andrew Schwabe
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

// Moodle coding-standard pass + cross-version validation for Marketplace submission (DEC-073).
// DEC-056: add get_user_demographics WS + custom_field_map setting for the
// post-consent demographics pre-fill (consent v1.1 on the backend).
$plugin->version   = 2026082801;
$plugin->requires  = 2024100700;      // Hard minimum: Moodle 4.5 LTS.
$plugin->supported = [405, 502];      // Advisory tested range: 4.5 (405) through 5.2 (502).
$plugin->component = 'local_srl_advisor';
$plugin->maturity  = MATURITY_BETA;
$plugin->release   = 'v0.7.3-beta';
