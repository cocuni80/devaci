"""Cobra object builders, grouped by ACI domain.

Each handler is registered under the top-level YAML/template key it handles.
Migrated from ``devaci._legacy.cobra``. Local variables keep the PascalCase
style of the Cobra SDK to mirror the managed-object class names.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import cobra.model.aaa
import cobra.model.bgp
import cobra.model.cdp
import cobra.model.comm
import cobra.model.coop
import cobra.model.ctrlr
import cobra.model.datetime
import cobra.model.ep
import cobra.model.fabric
import cobra.model.fv
import cobra.model.fvns
import cobra.model.geo
import cobra.model.igmp
import cobra.model.infra
import cobra.model.infrazone
import cobra.model.isis
import cobra.model.l2ext
import cobra.model.l3ext
import cobra.model.lacp
import cobra.model.latency
import cobra.model.lldp
import cobra.model.mcp
import cobra.model.mgmt
import cobra.model.phys
import cobra.model.pim
import cobra.model.pki
import cobra.model.pol
import cobra.model.qos
import cobra.model.snmp
import cobra.model.stormctrl
import cobra.model.stp
import cobra.model.vz

from devaci.cobra.base import not_nan_str
from devaci.cobra.registry import register

if TYPE_CHECKING:
    from devaci.cobra import CobraBuilder


# --------------------------------------------------------------------------- Tenant


@register("fvTenant")
def fv_tenant(builder: CobraBuilder, value: Any) -> None:
    """Tenants > All Tenants."""
    Uni = cobra.model.pol.Uni(builder.root)
    for fvTenant in value:
        builder.config.addMo(cobra.model.fv.Tenant(Uni, **fvTenant))


@register("fvAp")
def fv_ap(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Application Profiles."""
    Uni = cobra.model.pol.Uni(builder.root)
    for fvAp in value:
        if not_nan_str(fvAp, ["name", "tenant"]):
            Tenant = cobra.model.fv.Tenant(Uni, name=fvAp["tenant"])
            Ap = cobra.model.fv.Ap(Tenant, **fvAp)
            builder.config.addMo(Ap)


@register("fvAEPg")
def fv_aepg(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Application Profiles > Application EPGs."""
    Uni = cobra.model.pol.Uni(builder.root)
    for fvAEPg in value:
        Tenant = cobra.model.fv.Tenant(Uni, name=fvAEPg["tenant"])
        Ap = cobra.model.fv.Ap(Tenant, name=fvAEPg["fvApName"])
        AEPg = cobra.model.fv.AEPg(Ap, **fvAEPg)
        builder.config.addMo(AEPg)
        if "fvRsBd" in fvAEPg:
            if not_nan_str(fvAEPg["fvRsBd"], ["tnFvBDName"]):
                RsBd = cobra.model.fv.RsBd(AEPg, **fvAEPg["fvRsBd"])
                builder.config.addMo(RsBd)
        if "fvRsDomAtt" in fvAEPg:
            for fvRsDomAtt in fvAEPg["fvRsDomAtt"]:
                if not_nan_str(fvRsDomAtt, ["tDn"]):
                    RsDomAtt = cobra.model.fv.RsDomAtt(AEPg, **fvRsDomAtt)
                    builder.config.addMo(RsDomAtt)
        if "fvRsPathAtt" in fvAEPg:
            for fvRsPathAtt in fvAEPg["fvRsPathAtt"]:
                if not_nan_str(fvRsPathAtt, ["tDn", "primaryEncap", "mode"]):
                    RsPathAtt = cobra.model.fv.RsPathAtt(AEPg, **fvRsPathAtt)
                    builder.config.addMo(RsPathAtt)


@register("staticPath")
def static_path(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Application Profiles > Application EPGs > EPG Name > Static Ports."""
    Uni = cobra.model.pol.Uni(builder.root)
    for fvAp in value:
        Tenant = cobra.model.fv.Tenant(Uni, name=fvAp["tenant"])
        builder.config.addMo(Tenant)
        Ap = cobra.model.fv.Ap(Tenant, **fvAp)
        builder.config.addMo(Ap)
        if "fvAEPg" in fvAp:
            for fvAEPg in fvAp["fvAEPg"]:
                AEPg = cobra.model.fv.AEPg(Ap, **fvAEPg)
                if "fvRsPathAtt" in fvAEPg:
                    for fvRsPathAtt in fvAEPg["fvRsPathAtt"]:
                        RsPathAtt = cobra.model.fv.RsPathAtt(AEPg, **fvRsPathAtt)
                        builder.config.addMo(RsPathAtt)


@register("fvRsPathAtt")
def fv_rs_path_att(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Application Profiles > Application EPGs > EPG Name > Static Ports."""
    Uni = cobra.model.pol.Uni(builder.root)
    for fvRsPathAtt in value:
        if not_nan_str(
            fvRsPathAtt, ["tenant", "fvApName", "fvAEPgName", "tDn", "primaryEncap", "mode"]
        ):
            Tenant = cobra.model.fv.Tenant(Uni, name=fvRsPathAtt["tenant"])
            builder.config.addMo(Tenant)
            Ap = cobra.model.fv.Ap(Tenant, name=fvRsPathAtt["fvApName"])
            builder.config.addMo(Ap)
            AEPg = cobra.model.fv.AEPg(Ap, name=fvRsPathAtt["fvAEPgName"])
            builder.config.addMo(AEPg)
            RsPathAtt = cobra.model.fv.RsPathAtt(AEPg, **fvRsPathAtt)
            builder.config.addMo(RsPathAtt)


@register("tenant_application_uepg")
def tenant_application_uepg(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Application Profiles > uSeg EPGs."""
    for item in value:
        mo = item
        builder.config.addMo(mo)


@register("tenant_application_esg")
def tenant_application_esg(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Application Profiles > Endpoint Security Groups. TODO: implement."""
    pass


@register("fvBD")
def fv_bd(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Networking > Bridge Domains."""
    Uni = cobra.model.pol.Uni(builder.root)
    for fvBD in value:
        Tenant = cobra.model.fv.Tenant(Uni, name=fvBD["tenant"])
        BD = cobra.model.fv.BD(Tenant, **fvBD)
        builder.config.addMo(BD)
        if "fvRsCtx" in fvBD:
            if not_nan_str(fvBD["fvRsCtx"], ["tnFvCtxName"]):
                RsCtx = cobra.model.fv.RsCtx(BD, **fvBD["fvRsCtx"])
                builder.config.addMo(RsCtx)
        if "igmpIfP" in fvBD:
            if not_nan_str(fvBD["igmpIfP"], ["name"]):
                IfP = cobra.model.igmp.IfP(BD, **fvBD["igmpIfP"])
                builder.config.addMo(IfP)
        if "fvRsBdToEpRet" in fvBD:
            if not_nan_str(fvBD["fvRsBdToEpRet"], ["tnFvEpRetPolName"]):
                RsBdToEpRet = cobra.model.fv.RsBdToEpRet(BD, **fvBD["fvRsBdToEpRet"])
                builder.config.addMo(RsBdToEpRet)
        if "fvRsIgmpsn" in fvBD:
            if not_nan_str(fvBD["fvRsIgmpsn"], ["tnIgmpSnoopPolName"]):
                RsIgmpsn = cobra.model.fv.RsIgmpsn(BD, **fvBD["fvRsIgmpsn"])
                builder.config.addMo(RsIgmpsn)
        if "fvRsMldsn" in fvBD:
            if not_nan_str(fvBD["fvRsMldsn"], ["tnMldSnoopPolName"]):
                RsMldsn = cobra.model.fv.RsMldsn(BD, **fvBD["fvRsMldsn"])
                builder.config.addMo(RsMldsn)
        if "fvRsBDToOut" in fvBD:
            if not_nan_str(fvBD["fvRsBDToOut"], ["tnL3extOutName"]):
                RsBDToOut = cobra.model.fv.RsBDToOut(BD, **fvBD["fvRsBDToOut"])
                builder.config.addMo(RsBDToOut)
        if "fvSubnet" in fvBD:
            for fvSubnet in fvBD["fvSubnet"]:
                if not_nan_str(fvSubnet, ["ip"]):
                    Subnet = cobra.model.fv.Subnet(BD, **fvSubnet)
                    builder.config.addMo(Subnet)


@register("fvCtx")
def fv_ctx(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Networking > VRFs."""
    Uni = cobra.model.pol.Uni(builder.root)
    for fvCtx in value:
        Tenant = cobra.model.fv.Tenant(Uni, name=fvCtx["tenant"])
        Ctx = cobra.model.fv.Ctx(Tenant, **fvCtx)
        builder.config.addMo(Ctx)
        if "vzAny" in fvCtx:
            Any = cobra.model.vz.Any(Ctx, **fvCtx["vzAny"])
            builder.config.addMo(Any)
            if "vzRsAnyToProv" in fvCtx["vzAny"]:
                for vzRsAnyToProv in fvCtx["vzAny"]["vzRsAnyToProv"]:
                    if not_nan_str(vzRsAnyToProv, ["tnVzBrCPName"]):
                        RsAnyToProv = cobra.model.vz.RsAnyToProv(Any, **vzRsAnyToProv)
                        builder.config.addMo(RsAnyToProv)
            if "vzRsAnyToCons" in fvCtx["vzAny"]:
                for vzRsAnyToCons in fvCtx["vzAny"]["vzRsAnyToCons"]:
                    if not_nan_str(vzRsAnyToCons, ["tnVzBrCPName"]):
                        RsAnyToCons = cobra.model.vz.RsAnyToCons(Any, **vzRsAnyToCons)
                        builder.config.addMo(RsAnyToCons)
        if "fvRsCtxToEpRet" in fvCtx:
            if not_nan_str(fvCtx["fvRsCtxToEpRet"], ["tnFvEpRetPolName"]):
                RsCtxToEpRet = cobra.model.fv.RsCtxToEpRet(Ctx, **fvCtx["fvRsCtxToEpRet"])
                builder.config.addMo(RsCtxToEpRet)
        if "fvRsCtxToExtRouteTagPol" in fvCtx:
            if not_nan_str(fvCtx["fvRsCtxToExtRouteTagPol"], ["tnL3extRouteTagPolName"]):
                RsCtxToExtRouteTagPol = cobra.model.fv.RsCtxToExtRouteTagPol(
                    Ctx, **fvCtx["fvRsCtxToExtRouteTagPol"]
                )
                builder.config.addMo(RsCtxToExtRouteTagPol)
        if "fvRsOspfCtxPol" in fvCtx:
            if not_nan_str(fvCtx["fvRsOspfCtxPol"], ["tnOspfCtxPolName"]):
                RsOspfCtxPol = cobra.model.fv.RsOspfCtxPol(Ctx, **fvCtx["fvRsOspfCtxPol"])
                builder.config.addMo(RsOspfCtxPol)
        if "fvRsBgpCtxPol" in fvCtx:
            if not_nan_str(fvCtx["fvRsBgpCtxPol"], ["tnBgpCtxPolName"]):
                RsBgpCtxPol = cobra.model.fv.RsBgpCtxPol(Ctx, **fvCtx["fvRsBgpCtxPol"])
                builder.config.addMo(RsBgpCtxPol)
        if "fvRsVrfValidationPol" in fvCtx:
            if not_nan_str(fvCtx["fvRsVrfValidationPol"], ["tnL3extVrfValidationPolName"]):
                RsVrfValidationPol = cobra.model.fv.RsVrfValidationPol(
                    Ctx, **fvCtx["fvRsVrfValidationPol"]
                )
                builder.config.addMo(RsVrfValidationPol)
        if "pimCtxP" in fvCtx:
            if not_nan_str(fvCtx["pimCtxP"], ["mtu"]):
                CtxP = cobra.model.pim.CtxP(Ctx, **fvCtx["pimCtxP"])
                builder.config.addMo(CtxP)


@register("tenant_network_l2out")
def tenant_network_l2out(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Networking > L2Outs. TODO: implement."""
    pass


@register("l3extOut")
def l3ext_out(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Networking > L3Outs. TODO: implement."""
    pass


@register("tenant_network_srmpls_l3out")
def tenant_network_srmpls_l3out(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Networking > SR-MPLS VRF L3Outs. TODO: implement."""
    pass


@register("tenant_dot1q_tunnel")
def tenant_dot1q_tunnel(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Networking > Dot1Q Tunnels. TODO: implement."""
    pass


@register("fvnsAddrInst")
def fvns_addr_inst(builder: CobraBuilder, value: Any) -> None:
    """Tenants > mgmt > IP Address Pools."""
    Uni = cobra.model.pol.Uni(builder.root)
    for fvnsAddrInst in value:
        Tenant = cobra.model.fv.Tenant(Uni, name=fvnsAddrInst["tenant"])
        AddrInst = cobra.model.fvns.AddrInst(Tenant, **fvnsAddrInst)
        builder.config.addMo(AddrInst)
        if "fvnsUcastAddrBlk" in fvnsAddrInst:
            for fvnsUcastAddrBlk in fvnsAddrInst["fvnsUcastAddrBlk"]:
                if not_nan_str(fvnsUcastAddrBlk, ["from"]):
                    UcastAddrBlk = cobra.model.fvns.UcastAddrBlk(AddrInst, **fvnsUcastAddrBlk)
                    builder.config.addMo(UcastAddrBlk)


@register("mgmtGrp")
def mgmt_grp(builder: CobraBuilder, value: Any) -> None:
    """Tenants > mgmt > Managed Node Connectivity Groups."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    FuncP = cobra.model.infra.FuncP(Infra)
    for mgmtGrp in value:
        Grp = cobra.model.mgmt.Grp(FuncP, **mgmtGrp)
        builder.config.addMo(Grp)
        if "mgmtOoBZone" in mgmtGrp:
            OoBZone = cobra.model.mgmt.OoBZone(Grp)
            if "mgmtRsOoB" in mgmtGrp["mgmtOoBZone"]:
                RsOoB = cobra.model.mgmt.RsOoB(OoBZone, **mgmtGrp["mgmtOoBZone"]["mgmtRsOoB"])
                builder.config.addMo(RsOoB)
            if "mgmtRsAddrInst" in mgmtGrp["mgmtOoBZone"]:
                RsAddrInst = cobra.model.mgmt.RsAddrInst(
                    OoBZone, **mgmtGrp["mgmtOoBZone"]["mgmtRsAddrInst"]
                )
                builder.config.addMo(RsAddrInst)
        if "mgmtInBZone" in mgmtGrp:
            InBZone = cobra.model.mgmt.InBZone(Grp)
            if "mgmtRsInB" in mgmtGrp["mgmtInBZone"]:
                RsInB = cobra.model.mgmt.RsInB(InBZone, **mgmtGrp["mgmtInBZone"]["mgmtRsInB"])
                builder.config.addMo(RsInB)
            if "mgmtRsAddrInst" in mgmtGrp["mgmtInBZone"]:
                RsAddrInst = cobra.model.mgmt.RsAddrInst(
                    InBZone, **mgmtGrp["mgmtInBZone"]["mgmtRsAddrInst"]
                )
                builder.config.addMo(RsAddrInst)


@register("mgmtNodeGrp")
def mgmt_node_grp(builder: CobraBuilder, value: Any) -> None:
    """Tenants > mgmt > Node Management Addresses."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    for mgmtNodeGrp in value:
        NodeGrp = cobra.model.mgmt.NodeGrp(Infra, **mgmtNodeGrp)
        builder.config.addMo(NodeGrp)
        if "mgmtRsGrp" in mgmtNodeGrp:
            for mgmtRsGrp in mgmtNodeGrp["mgmtRsGrp"]:
                RsGrp = cobra.model.mgmt.RsGrp(NodeGrp, **mgmtRsGrp)
                builder.config.addMo(RsGrp)
        if "infraNodeBlk" in mgmtNodeGrp:
            for infraNodeBlk in mgmtNodeGrp["infraNodeBlk"]:
                if not_nan_str(infraNodeBlk, ["from_"]):
                    NodeBlk = cobra.model.infra.NodeBlk(NodeGrp, **infraNodeBlk)
                    builder.config.addMo(NodeBlk)


@register("tenant_contract_standard")
def tenant_contract_standard(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Contracts > Standard. TODO: implement."""
    pass


@register("tenant_contract_taboo")
def tenant_contract_taboo(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Contracts > Taboos. TODO: implement."""
    pass


@register("tenant_contract_imported")
def tenant_contract_imported(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Contracts > Imported. TODO: implement."""
    pass


@register("tenant_contract_filter")
def tenant_contract_filter(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Contracts > Filters. TODO: implement."""
    pass


@register("tenant_contract_oob")
def tenant_contract_oob(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Contracts > Out-Of-Band Contracts. TODO: implement."""
    pass


@register("tenant_policy_protocol_bfd")
def tenant_policy_protocol_bfd(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Protocol > BFD. TODO: implement."""
    pass


@register("tenant_policy_protocol_bgp")
def tenant_policy_protocol_bgp(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Protocol > BGP. TODO: implement."""
    pass


@register("tenant_policy_protocol_qos")
def tenant_policy_protocol_qos(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Protocol > Custom QoS. TODO: implement."""
    pass


@register("tenant_policy_protocol_dhcp")
def tenant_policy_protocol_dhcp(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Protocol > DHCP. TODO: implement."""
    pass


@register("tenant_policy_protocol_dataplane")
def tenant_policy_protocol_dataplane(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Protocol > Data Plane Policing. TODO: implement."""
    pass


@register("tenant_policy_protocol_eigrp")
def tenant_policy_protocol_eigrp(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Protocol > EIGRP. TODO: implement."""
    pass


@register("tenant_policy_protocol_endpoint_retention")
def tenant_policy_protocol_endpoint_retention(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Protocol > End Point Retention. TODO: implement."""
    pass


@register("tenant_policy_protocol_firsthop_security")
def tenant_policy_protocol_firsthop_security(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Protocol > First Hop Security. TODO: implement."""
    pass


@register("tenant_policy_protocol_hsrp")
def tenant_policy_protocol_hsrp(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Protocol > HSRP. TODO: implement."""
    pass


@register("tenant_policy_protocol_igmp")
def tenant_policy_protocol_igmp(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Protocol > IGMP. TODO: implement."""
    pass


@register("tenant_policy_protocol_ip_sla")
def tenant_policy_protocol_ip_sla(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Protocol > IP SLA. TODO: implement."""
    pass


@register("tenant_policy_protocol_pbr")
def tenant_policy_protocol_pbr(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Protocol > L4-L7 Policy-Based Redirect. TODO: implement."""
    pass


@register("tenant_policy_protocol_ospf")
def tenant_policy_protocol_ospf(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Protocol > OSPF. TODO: implement."""
    pass


@register("tenant_policy_protocol_pim")
def tenant_policy_protocol_pim(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Protocol > PIM. TODO: implement."""
    pass


@register("tenant_policy_protocol_routemap_multicast")
def tenant_policy_protocol_routemap_multicast(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Protocol > Route Maps for Multicast. TODO: implement."""
    pass


@register("tenant_policy_protocol_routemap_control")
def tenant_policy_protocol_routemap_control(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Protocol > Route Maps for Route Control. TODO: implement."""
    pass


@register("tenant_policy_protocol_route_tag")
def tenant_policy_protocol_route_tag(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Protocol > Route Tag. TODO: implement."""
    pass


@register("tenant_policy_troubleshooting_span")
def tenant_policy_troubleshooting_span(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Troubleshooting SPAN. TODO: implement."""
    pass


@register("tenant_policy_troubleshooting_traceroute")
def tenant_policy_troubleshooting_traceroute(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Troubleshooting Traceroute. TODO: implement."""
    pass


@register("tenant_policy_monitoring")
def tenant_policy_monitoring(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Monitoring. TODO: implement."""
    pass


@register("tenant_policy_netflow")
def tenant_policy_netflow(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > NetFlow. TODO: implement."""
    pass


@register("tenant_policy_vmm")
def tenant_policy_vmm(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > VMM. TODO: implement."""
    pass


@register("tenant_service_parameter")
def tenant_service_parameter(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Services > L4-L7 > Service Parameters. TODO: implement."""
    pass


@register("tenant_service_graph_template")
def tenant_service_graph_template(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Services > L4-L7 > Service Graph Templates. TODO: implement."""
    pass


@register("tenant_service_router_configuration")
def tenant_service_router_configuration(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Services > L4-L7 > Router Configuration. TODO: implement."""
    pass


@register("tenant_service_function_profile")
def tenant_service_function_profile(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Services > L4-L7 > Function Profiles. TODO: implement."""
    pass


@register("tenant_service_devices")
def tenant_service_devices(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Services > L4-L7 > Devices. TODO: implement."""
    pass


@register("tenant_service_imported_device")
def tenant_service_imported_device(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Services > L4-L7 > Imported Devices. TODO: implement."""
    pass


@register("tenant_service_device_policy")
def tenant_service_device_policy(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Services > L4-L7 > Device Selection Policies. TODO: implement."""
    pass


@register("tenant_service_deployed_graph_instance")
def tenant_service_deployed_graph_instance(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Services > L4-L7 > Deployed Graph Instances. TODO: implement."""
    pass


@register("tenant_service_deployed_device")
def tenant_service_deployed_device(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Services > L4-L7 > Deployed Devices. TODO: implement."""
    pass


@register("tenant_service_device_manager")
def tenant_service_device_manager(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Services > L4-L7 > Device Managers. TODO: implement."""
    pass


@register("tenant_service_chassis")
def tenant_service_chassis(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Services > L4-L7 > Chassis. TODO: implement."""
    pass


@register("tenant_node_management_epg")
def tenant_node_management_epg(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Node Management EPGs. TODO: implement."""
    pass


@register("tenant_external_management_profile")
def tenant_external_management_profile(builder: CobraBuilder, value: Any) -> None:
    """Tenants > External Management Network Instance Profiles. TODO: implement."""
    pass


@register("tenant_node_management_address")
def tenant_node_management_address(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Node Management Address. TODO: implement."""
    pass


@register("tenant_node_management_static")
def tenant_node_management_static(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Node Management Address > Static Node Management Address. TODO: implement."""
    pass


@register("tenant_node_connection_group")
def tenant_node_connection_group(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Managed Node Connectivity Groups. TODO: implement."""
    pass


# --------------------------------------------------------------------------- Fabric


@register("fabricSetupPol")
def fabric_setup_pol(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Inventory > Pod Fabric Setup Policy."""
    Uni = cobra.model.pol.Uni(builder.root)
    Inst = cobra.model.ctrlr.Inst(Uni)
    for fabricSetupPol in value:
        SetupPol = cobra.model.fabric.SetupPol(Inst, **fabricSetupPol)
        builder.config.addMo(SetupPol)
        if "fabricSetupP" in fabricSetupPol:
            for fabricSetupP in fabricSetupPol["fabricSetupP"]:
                SetupP = cobra.model.fabric.SetupP(SetupPol, **fabricSetupP)
                builder.config.addMo(SetupP)


@register("fabricRsOosPath")
def fabric_rs_oos_path(builder: CobraBuilder, value: Any) -> None:
    """Fabric > RsOosPath."""
    Uni = cobra.model.pol.Uni(builder.root)
    Inst = cobra.model.fabric.Inst(Uni)
    OOServicePol = cobra.model.fabric.OOServicePol(Inst)
    for fabricRsOosPath in value:
        RsOosPath = cobra.model.fabric.RsOosPath(OOServicePol, **fabricRsOosPath)
        builder.config.addMo(RsOosPath)


@register("fabricSetupP")
def fabric_setup_p(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Inventory > Pod Fabric Setup Policy."""
    Uni = cobra.model.pol.Uni(builder.root)
    Inst = cobra.model.ctrlr.Inst(Uni)
    SetupPol = cobra.model.fabric.SetupPol(Inst)
    builder.config.addMo(SetupPol)
    for fabricSetupP in value:
        SetupP = cobra.model.fabric.SetupP(SetupPol, **fabricSetupP)
        builder.config.addMo(SetupP)


@register("fabricNodeIdentPol")
def fabric_node_ident_pol(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Inventory > Fabric Membership."""
    Uni = cobra.model.pol.Uni(builder.root)
    Inst = cobra.model.ctrlr.Inst(Uni)
    for fabricNodeIdentPol in value:
        NodeIdentPol = cobra.model.fabric.NodeIdentPol(Inst, **fabricNodeIdentPol)
        builder.config.addMo(NodeIdentPol)
        if "fabricNodeIdentP" in fabricNodeIdentPol:
            for fabricNodeIdentP in fabricNodeIdentPol["fabricNodeIdentP"]:
                NodeIdentP = cobra.model.fabric.NodeIdentP(NodeIdentPol, **fabricNodeIdentP)
                builder.config.addMo(NodeIdentP)


@register("fabricPodPGrp")
def fabric_pod_p_grp(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Fabric Policies > Pods > Policy Groups."""
    for item in value:
        fabric_inst = cobra.model.fabric.Inst(builder.uni)
        fabric_func_p = cobra.model.fabric.FuncP(fabric_inst)
        mo = cobra.model.fabric.PodPGrp(fabric_func_p, **item)
        if "fabricRtPodPGrp" in item:
            cobra.model.fabric.RtPodPGrp(mo, **item["fabricRtPodPGrp"])
        if "fabricRsSnmpPol" in item:
            cobra.model.fabric.RsSnmpPol(mo, **item["fabricRsSnmpPol"])
        if "fabricRsPodPGrpIsisDomP" in item:
            cobra.model.fabric.RsPodPGrpIsisDomP(mo, **item["fabricRsPodPGrpIsisDomP"])
        if "fabricRsPodPGrpCoopP" in item:
            cobra.model.fabric.RsPodPGrpCoopP(mo, **item["fabricRsPodPGrpCoopP"])
        if "fabricRsPodPGrpBGPRRP" in item:
            cobra.model.fabric.RsPodPGrpBGPRRP(mo, **item["fabricRsPodPGrpBGPRRP"])
        if "fabricRsTimePol" in item:
            cobra.model.fabric.RsTimePol(mo, **item["fabricRsTimePol"])
        if "fabricRsMacsecPol" in item:
            cobra.model.fabric.RsMacsecPol(mo, **item["fabricRsMacsecPol"])
        if "fabricRsCommPol" in item:
            cobra.model.fabric.RsCommPol(mo, **item["fabricRsCommPol"])
        builder.config.addMo(mo)


@register("fabricPodP")
def fabric_pod_p(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Fabric Policies > Pods > Profiles."""
    for item in value:
        fabric_inst = cobra.model.fabric.Inst(builder.uni)
        mo = cobra.model.fabric.PodP(fabric_inst, **item)
        if "fabricPodS" in item:
            for pod_s in item["fabricPodS"]:
                mo_pod_s = cobra.model.fabric.PodS(mo, **pod_s)
                if "fabricRsPodPGrp" in pod_s:
                    cobra.model.fabric.RsPodPGrp(mo_pod_s, **pod_s["fabricRsPodPGrp"])
                if "fabricPodBlk" in pod_s:
                    cobra.model.fabric.PodBlk(mo_pod_s, **pod_s["fabricPodBlk"])
        builder.config.addMo(mo)


@register("fabric_switch_leaf_profile")
def fabric_switch_leaf_profile(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Fabric Policies > Switches > Leaf Switches > Profiles. TODO: implement."""
    pass


@register("fabric_switch_leaf_policy_group")
def fabric_switch_leaf_policy_group(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Fabric Policies > Switches > Leaf Switches > Policy Groups. TODO: implement."""
    pass


@register("fabric_switch_spine_profile")
def fabric_switch_spine_profile(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Fabric Policies > Switches > Spine Switches > Profiles. TODO: implement."""
    pass


@register("fabric_switch_spine_policy_group")
def fabric_switch_spine_policy_group(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Fabric Policies > Switches > Spine Switches > Policy Groups. TODO: implement."""
    pass


@register("fabric_module_leaf_profile")
def fabric_module_leaf_profile(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Fabric Policies > Modules > Leaf Modules > Profiles. TODO: implement."""
    pass


@register("fabric_module_leaf_policy_group")
def fabric_module_leaf_policy_group(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Fabric Policies > Modules > Leaf Modules > Policy Groups. TODO: implement."""
    pass


@register("fabric_module_spine_profile")
def fabric_module_spine_profile(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Fabric Policies > Modules > Spine Modules > Profiles. TODO: implement."""
    pass


@register("fabric_module_spine_policy_group")
def fabric_module_spine_policy_group(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Fabric Policies > Modules > Spine Modules > Policy Groups. TODO: implement."""
    pass


@register("fabric_interface_leaf_profile")
def fabric_interface_leaf_profile(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Fabric Policies > Interfaces > Leaf Interfaces > Profiles. TODO: implement."""
    pass


@register("fabric_interface_leaf_policy_group")
def fabric_interface_leaf_policy_group(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Fabric Policies > Interfaces > Leaf Interfaces > Policy Groups. TODO: implement."""
    pass


@register("fabric_interface_spine_profile")
def fabric_interface_spine_profile(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Fabric Policies > Interfaces > Spine Interfaces > Profiles. TODO: implement."""
    pass


@register("fabric_interface_spine_policy_group")
def fabric_interface_spine_policy_group(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Fabric Policies > Interfaces > Spine Interfaces > Policy Groups. TODO: implement."""
    pass


@register("datetimePol")
def datetime_pol(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Fabric Policies > Policies > Pod > Date and Time."""
    Inst = cobra.model.fabric.Inst(builder.uni)
    for datetimePol in value:
        Pol = cobra.model.datetime.Pol(Inst, **datetimePol)
        builder.config.addMo(Pol)
        if "datetimeNtpAuthKey" in datetimePol:
            for datetimeNtpAuthKey in datetimePol["datetimeNtpAuthKey"]:
                if not_nan_str(datetimeNtpAuthKey, ["id", "key", "trusted", "keyType"]):
                    NtpAuthKey = cobra.model.datetime.NtpAuthKey(Pol, **datetimeNtpAuthKey)
                    builder.config.addMo(NtpAuthKey)
        if "datetimeNtpProv" in datetimePol:
            for datetimeNtpProv in datetimePol["datetimeNtpProv"]:
                if not_nan_str(datetimeNtpProv, ["name"]):
                    NtpProv = cobra.model.datetime.NtpProv(Pol, **datetimeNtpProv)
                    builder.config.addMo(NtpProv)
                    if "datetimeRsNtpProvToNtpAuthKey" in datetimeNtpProv:
                        for key in datetimeNtpProv["datetimeRsNtpProvToNtpAuthKey"]:
                            if not_nan_str(key, ["tnDatetimeNtpAuthKeyId"]):
                                RsNtpProvToNtpAuthKey = cobra.model.datetime.RsNtpProvToNtpAuthKey(
                                    NtpProv, **key
                                )
                                builder.config.addMo(RsNtpProvToNtpAuthKey)
                    if "datetimeRsNtpProvToEpg" in datetimeNtpProv:
                        if not_nan_str(datetimeNtpProv["datetimeRsNtpProvToEpg"], ["tDn"]):
                            RsNtpProvToEpg = cobra.model.datetime.RsNtpProvToEpg(
                                NtpProv, **datetimeNtpProv["datetimeRsNtpProvToEpg"]
                            )
                            builder.config.addMo(RsNtpProvToEpg)


@register("snmpPol")
def snmp_pol(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Fabric Policies > Policies > Pod > SNMP."""
    Inst = cobra.model.fabric.Inst(builder.uni)
    for snmpPol in value:
        if not_nan_str(snmpPol, ["name"]):
            Pol = cobra.model.snmp.Pol(Inst, **snmpPol)
            builder.config.addMo(Pol)
            if "snmpClientGrpP" in snmpPol:
                for snmpClientGrpP in snmpPol["snmpClientGrpP"]:
                    if not_nan_str(snmpClientGrpP, ["name"]):
                        ClientGrpP = cobra.model.snmp.ClientGrpP(Pol, **snmpClientGrpP)
                        if "snmpRsEpg" in snmpClientGrpP:
                            if not_nan_str(snmpClientGrpP["snmpRsEpg"], ["tDn"]):
                                RsEpg = cobra.model.snmp.RsEpg(
                                    ClientGrpP, **snmpClientGrpP["snmpRsEpg"]
                                )
                                builder.config.addMo(RsEpg)
                        if "snmpClientP" in snmpClientGrpP:
                            for snmpClientP in snmpClientGrpP["snmpClientP"]:
                                if not_nan_str(snmpClientP, ["name", "addr"]):
                                    ClientP = cobra.model.snmp.ClientP(ClientGrpP, **snmpClientP)
                                    builder.config.addMo(ClientP)
            if "snmpUserP" in snmpPol:
                for snmpUserP in snmpPol["snmpUserP"]:
                    if not_nan_str(
                        snmpUserP, ["name", "privType", "privKey", "authType", "authKey"]
                    ):
                        UserP = cobra.model.snmp.UserP(Pol, **snmpUserP)
                        builder.config.addMo(UserP)
            if "snmpCommunityP" in snmpPol:
                for snmpCommunityP in snmpPol["snmpCommunityP"]:
                    if not_nan_str(snmpCommunityP, ["name"]):
                        CommunityP = cobra.model.snmp.CommunityP(Pol, **snmpCommunityP)
                        builder.config.addMo(CommunityP)
            if "snmpTrapFwdServerP" in snmpPol:
                for snmpTrapFwdServerP in snmpPol["snmpTrapFwdServerP"]:
                    if not_nan_str(snmpTrapFwdServerP, ["addr", "port"]):
                        TrapFwdServerP = cobra.model.snmp.TrapFwdServerP(Pol, **snmpTrapFwdServerP)
                        builder.config.addMo(TrapFwdServerP)


@register("commPol")
def comm_pol(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Fabric Policies > Policies > Pod > Management Access."""
    Inst = cobra.model.fabric.Inst(builder.uni)
    for commPol in value:
        Pol = cobra.model.comm.Pol(Inst, **commPol)
        builder.config.addMo(Pol)
        if "commTelnet" in commPol:
            if not_nan_str(commPol["commTelnet"], ["name", "adminSt"]):
                Telnet = cobra.model.comm.Telnet(Pol, **commPol["commTelnet"])
                builder.config.addMo(Telnet)
        if "commSsh" in commPol:
            if not_nan_str(commPol["commSsh"], ["name", "adminSt"]):
                Ssh = cobra.model.comm.Ssh(Pol, **commPol["commSsh"])
                builder.config.addMo(Ssh)
        if "commHttp" in commPol:
            if not_nan_str(commPol["commHttp"], ["name", "adminSt"]):
                Http = cobra.model.comm.Http(Pol, **commPol["commHttp"])
                builder.config.addMo(Http)
        if "commHttps" in commPol:
            if not_nan_str(commPol["commHttps"], ["name", "adminSt"]):
                Https = cobra.model.comm.Https(Pol, **commPol["commHttps"])
                builder.config.addMo(Https)
        if "commShellinabox" in commPol:
            if not_nan_str(commPol["commShellinabox"], ["name", "adminSt"]):
                Shellinabox = cobra.model.comm.Shellinabox(Pol, **commPol["commShellinabox"])
                builder.config.addMo(Shellinabox)


@register("fabric_policy_switch_callhome")
def fabric_policy_switch_callhome(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Fabric Policies > Policies > Switch > Callhome Inventory. TODO: implement."""
    pass


# --------------------------------------------------------------------------- Infra


@register("infraNodeP")
def infra_node_p(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Switches > Leaf Switches > Profiles."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    for infraNodeP in value:
        NodeP = cobra.model.infra.NodeP(Infra, **infraNodeP)
        builder.config.addMo(NodeP)
        if "infraLeafS" in infraNodeP:
            for infraLeafS in infraNodeP["infraLeafS"]:
                if not_nan_str(infraLeafS, ["name"]):
                    LeafS = cobra.model.infra.LeafS(NodeP, **infraLeafS)
                    builder.config.addMo(LeafS)
                    if "infraNodeBlk" in infraLeafS:
                        if not_nan_str(infraLeafS["infraNodeBlk"], ["from_"]):
                            NodeBlk = cobra.model.infra.NodeBlk(LeafS, **infraLeafS["infraNodeBlk"])
                            builder.config.addMo(NodeBlk)
                    if "infraRsAccNodePGrp" in infraLeafS:
                        if not_nan_str(infraLeafS["infraRsAccNodePGrp"], ["tDn"]):
                            RsAccNodePGrp = cobra.model.infra.RsAccNodePGrp(
                                LeafS, **infraLeafS["infraRsAccNodePGrp"]
                            )
                            builder.config.addMo(RsAccNodePGrp)
        if "infraRsAccPortP" in infraNodeP:
            for infraRsAccPortP in infraNodeP["infraRsAccPortP"]:
                if not_nan_str(infraRsAccPortP, ["tDn"]):
                    RsAccPortP = cobra.model.infra.RsAccPortP(NodeP, **infraRsAccPortP)
                    builder.config.addMo(RsAccPortP)


@register("infraAccNodePGrp")
def infra_acc_node_p_grp(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Switches > Leaf Switches > Policy Groups."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    FuncP = cobra.model.infra.FuncP(Infra)
    for infraAccNodePGrp in value:
        AccNodePGrp = cobra.model.infra.AccNodePGrp(FuncP, **infraAccNodePGrp)
        builder.config.addMo(AccNodePGrp)
        if "infraRsTopoctrlFwdScaleProfPol" in infraAccNodePGrp:
            if not_nan_str(
                infraAccNodePGrp["infraRsTopoctrlFwdScaleProfPol"],
                ["tnTopoctrlFwdScaleProfilePolName"],
            ):
                RsTopoctrlFwdScaleProfPol = cobra.model.infra.RsTopoctrlFwdScaleProfPol(
                    AccNodePGrp, **infraAccNodePGrp["infraRsTopoctrlFwdScaleProfPol"]
                )
                builder.config.addMo(RsTopoctrlFwdScaleProfPol)
        if "infraRsLeafTopoctrlUsbConfigProfilePol" in infraAccNodePGrp:
            if not_nan_str(
                infraAccNodePGrp["infraRsLeafTopoctrlUsbConfigProfilePol"],
                ["tnTopoctrlUsbConfigProfilePolName"],
            ):
                RsLeafTopoctrlUsbConfigProfilePol = (
                    cobra.model.infra.RsLeafTopoctrlUsbConfigProfilePol(
                        AccNodePGrp,
                        **infraAccNodePGrp["infraRsLeafTopoctrlUsbConfigProfilePol"],
                    )
                )
                builder.config.addMo(RsLeafTopoctrlUsbConfigProfilePol)
        if "infraRsLeafPGrpToLldpIfPol" in infraAccNodePGrp:
            if not_nan_str(infraAccNodePGrp["infraRsLeafPGrpToLldpIfPol"], ["tnLldpIfPolName"]):
                RsLeafPGrpToLldpIfPol = cobra.model.infra.RsLeafPGrpToLldpIfPol(
                    AccNodePGrp, **infraAccNodePGrp["infraRsLeafPGrpToLldpIfPol"]
                )
                builder.config.addMo(RsLeafPGrpToLldpIfPol)
        if "infraRsBfdIpv6InstPol" in infraAccNodePGrp:
            if not_nan_str(infraAccNodePGrp["infraRsBfdIpv6InstPol"], ["tnBfdIpv6InstPolName"]):
                RsBfdIpv6InstPol = cobra.model.infra.RsBfdIpv6InstPol(
                    AccNodePGrp, **infraAccNodePGrp["infraRsBfdIpv6InstPol"]
                )
                builder.config.addMo(RsBfdIpv6InstPol)
        if "infraRsSynceInstPol" in infraAccNodePGrp:
            if not_nan_str(infraAccNodePGrp["infraRsSynceInstPol"], ["tnSynceInstPolName"]):
                RsSynceInstPol = cobra.model.infra.RsSynceInstPol(
                    AccNodePGrp, **infraAccNodePGrp["infraRsSynceInstPol"]
                )
                builder.config.addMo(RsSynceInstPol)
        if "infraRsPoeInstPol" in infraAccNodePGrp:
            if not_nan_str(infraAccNodePGrp["infraRsPoeInstPol"], ["tnPoeInstPolName"]):
                RsPoeInstPol = cobra.model.infra.RsPoeInstPol(
                    AccNodePGrp, **infraAccNodePGrp["infraRsPoeInstPol"]
                )
                builder.config.addMo(RsPoeInstPol)
        if "infraRsBfdMhIpv4InstPol" in infraAccNodePGrp:
            if not_nan_str(infraAccNodePGrp["infraRsBfdMhIpv4InstPol"], ["tnBfdMhIpv4InstPolName"]):
                RsBfdMhIpv4InstPol = cobra.model.infra.RsBfdMhIpv4InstPol(
                    AccNodePGrp, **infraAccNodePGrp["infraRsBfdMhIpv4InstPol"]
                )
                builder.config.addMo(RsBfdMhIpv4InstPol)
        if "infraRsBfdMhIpv6InstPol" in infraAccNodePGrp:
            if not_nan_str(infraAccNodePGrp["infraRsBfdMhIpv6InstPol"], ["tnBfdMhIpv6InstPolName"]):
                RsBfdMhIpv6InstPol = cobra.model.infra.RsBfdMhIpv6InstPol(
                    AccNodePGrp, **infraAccNodePGrp["infraRsBfdMhIpv6InstPol"]
                )
                builder.config.addMo(RsBfdMhIpv6InstPol)
        if "infraRsEquipmentFlashConfigPol" in infraAccNodePGrp:
            if not_nan_str(
                infraAccNodePGrp["infraRsEquipmentFlashConfigPol"],
                ["tnEquipmentFlashConfigPolName"],
            ):
                RsEquipmentFlashConfigPol = cobra.model.infra.RsEquipmentFlashConfigPol(
                    AccNodePGrp, **infraAccNodePGrp["infraRsEquipmentFlashConfigPol"]
                )
                builder.config.addMo(RsEquipmentFlashConfigPol)
        if "infraRsMonNodeInfraPol" in infraAccNodePGrp:
            if not_nan_str(infraAccNodePGrp["infraRsMonNodeInfraPol"], ["tnMonInfraPolName"]):
                RsMonNodeInfraPol = cobra.model.infra.RsMonNodeInfraPol(
                    AccNodePGrp, **infraAccNodePGrp["infraRsMonNodeInfraPol"]
                )
                builder.config.addMo(RsMonNodeInfraPol)
        if "infraRsFcInstPol" in infraAccNodePGrp:
            if not_nan_str(infraAccNodePGrp["infraRsFcInstPol"], ["tnFcInstPolName"]):
                RsFcInstPol = cobra.model.infra.RsFcInstPol(
                    AccNodePGrp, **infraAccNodePGrp["infraRsFcInstPol"]
                )
                builder.config.addMo(RsFcInstPol)
        if "infraRsTopoctrlFastLinkFailoverInstPol" in infraAccNodePGrp:
            if not_nan_str(
                infraAccNodePGrp["infraRsTopoctrlFastLinkFailoverInstPol"],
                ["tnTopoctrlFastLinkFailoverInstPolName"],
            ):
                RsTopoctrlFastLinkFailoverInstPol = (
                    cobra.model.infra.RsTopoctrlFastLinkFailoverInstPol(
                        AccNodePGrp,
                        **infraAccNodePGrp["infraRsTopoctrlFastLinkFailoverInstPol"],
                    )
                )
                builder.config.addMo(RsTopoctrlFastLinkFailoverInstPol)
        if "infraRsMstInstPol" in infraAccNodePGrp:
            if not_nan_str(infraAccNodePGrp["infraRsMstInstPol"], ["tnStpInstPolName"]):
                RsMstInstPol = cobra.model.infra.RsMstInstPol(
                    AccNodePGrp, **infraAccNodePGrp["infraRsMstInstPol"]
                )
                builder.config.addMo(RsMstInstPol)
        if "infraRsFcFabricPol" in infraAccNodePGrp:
            if not_nan_str(infraAccNodePGrp["infraRsFcFabricPol"], ["tnFcFabricPolName"]):
                RsFcFabricPol = cobra.model.infra.RsFcFabricPol(
                    AccNodePGrp, **infraAccNodePGrp["infraRsFcFabricPol"]
                )
                builder.config.addMo(RsFcFabricPol)
        if "infraRsLeafCoppProfile" in infraAccNodePGrp:
            if not_nan_str(infraAccNodePGrp["infraRsLeafCoppProfile"], ["tnCoppLeafProfileName"]):
                RsLeafCoppProfile = cobra.model.infra.RsLeafCoppProfile(
                    AccNodePGrp, **infraAccNodePGrp["infraRsLeafCoppProfile"]
                )
                builder.config.addMo(RsLeafCoppProfile)
        if "infraRsIaclLeafProfile" in infraAccNodePGrp:
            if not_nan_str(infraAccNodePGrp["infraRsIaclLeafProfile"], ["tnIaclLeafProfileName"]):
                RsIaclLeafProfile = cobra.model.infra.RsIaclLeafProfile(
                    AccNodePGrp, **infraAccNodePGrp["infraRsIaclLeafProfile"]
                )
                builder.config.addMo(RsIaclLeafProfile)
        if "infraRsBfdIpv4InstPol" in infraAccNodePGrp:
            if not_nan_str(infraAccNodePGrp["infraRsBfdIpv4InstPol"], ["tnBfdIpv4InstPolName"]):
                RsBfdIpv4InstPol = cobra.model.infra.RsBfdIpv4InstPol(
                    AccNodePGrp, **infraAccNodePGrp["infraRsBfdIpv4InstPol"]
                )
                builder.config.addMo(RsBfdIpv4InstPol)
        if "infraRsL2NodeAuthPol" in infraAccNodePGrp:
            if not_nan_str(infraAccNodePGrp["infraRsL2NodeAuthPol"], ["tnL2NodeAuthPolName"]):
                RsL2NodeAuthPol = cobra.model.infra.RsL2NodeAuthPol(
                    AccNodePGrp, **infraAccNodePGrp["infraRsL2NodeAuthPol"]
                )
                builder.config.addMo(RsL2NodeAuthPol)
        if "infraRsLeafPGrpToCdpIfPol" in infraAccNodePGrp:
            if not_nan_str(infraAccNodePGrp["infraRsLeafPGrpToCdpIfPol"], ["tnCdpIfPolName"]):
                RsLeafPGrpToCdpIfPol = cobra.model.infra.RsLeafPGrpToCdpIfPol(
                    AccNodePGrp, **infraAccNodePGrp["infraRsLeafPGrpToCdpIfPol"]
                )
                builder.config.addMo(RsLeafPGrpToCdpIfPol)


@register("infraSpineP")
def infra_spine_p(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Switches > Spine Switches > Profiles."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    for infraSpineP in value:
        SpineP = cobra.model.infra.SpineP(Infra, **infraSpineP)
        builder.config.addMo(SpineP)
        if "infraSpineS" in infraSpineP:
            for infraSpineS in infraSpineP["infraSpineS"]:
                SpineS = cobra.model.infra.SpineS(SpineP, **infraSpineS)
                builder.config.addMo(SpineS)
                if "infraRsSpineAccNodePGrp" in infraSpineS:
                    RsSpineAccNodePGrp = cobra.model.infra.RsSpineAccNodePGrp(
                        SpineS, **infraSpineS["infraRsSpineAccNodePGrp"]
                    )
                    builder.config.addMo(RsSpineAccNodePGrp)
                if "infraNodeBlk" in infraSpineS:
                    NodeBlk = cobra.model.infra.NodeBlk(SpineS, **infraSpineS["infraNodeBlk"])
                    builder.config.addMo(NodeBlk)
        if "infraRsSpAccPortP" in infraSpineP:
            RsSpAccPortP = cobra.model.infra.RsSpAccPortP(
                SpineP, **infraSpineP["infraRsSpAccPortP"]
            )
            builder.config.addMo(RsSpAccPortP)


@register("infraSpineAccNodePGrp")
def infra_spine_acc_node_p_grp(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Switches > Spine Switches > Policy Groups."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    FuncP = cobra.model.infra.FuncP(Infra)
    for infraSpineAccNodePGrp in value:
        SpineAccNodePGrp = cobra.model.infra.SpineAccNodePGrp(FuncP, **infraSpineAccNodePGrp)
        builder.config.addMo(SpineAccNodePGrp)
        if "infraRsSpineCoppProfile" in infraSpineAccNodePGrp:
            RsSpineCoppProfile = cobra.model.infra.RsSpineCoppProfile(
                SpineAccNodePGrp, **infraSpineAccNodePGrp["infraRsSpineCoppProfile"]
            )
            builder.config.addMo(RsSpineCoppProfile)
        if "infraRsSpineBfdIpv4InstPol" in infraSpineAccNodePGrp:
            RsSpineBfdIpv4InstPol = cobra.model.infra.RsSpineBfdIpv4InstPol(
                SpineAccNodePGrp, **infraSpineAccNodePGrp["infraRsSpineBfdIpv4InstPol"]
            )
            builder.config.addMo(RsSpineBfdIpv4InstPol)
        if "infraRsSpineBfdIpv6InstPol" in infraSpineAccNodePGrp:
            RsSpineBfdIpv6InstPol = cobra.model.infra.RsSpineBfdIpv6InstPol(
                SpineAccNodePGrp, **infraSpineAccNodePGrp["infraRsSpineBfdIpv6InstPol"]
            )
            builder.config.addMo(RsSpineBfdIpv6InstPol)
        if "infraRsIaclSpineProfile" in infraSpineAccNodePGrp:
            RsIaclSpineProfile = cobra.model.infra.RsIaclSpineProfile(
                SpineAccNodePGrp, **infraSpineAccNodePGrp["infraRsIaclSpineProfile"]
            )
            builder.config.addMo(RsIaclSpineProfile)
        if "infraRsSpinePGrpToCdpIfPol" in infraSpineAccNodePGrp:
            RsSpinePGrpToCdpIfPol = cobra.model.infra.RsSpinePGrpToCdpIfPol(
                SpineAccNodePGrp, **infraSpineAccNodePGrp["infraRsSpinePGrpToCdpIfPol"]
            )
            builder.config.addMo(RsSpinePGrpToCdpIfPol)
        if "infraRsSpinePGrpToLldpIfPol" in infraSpineAccNodePGrp:
            RsSpinePGrpToLldpIfPol = cobra.model.infra.RsSpinePGrpToLldpIfPol(
                SpineAccNodePGrp, **infraSpineAccNodePGrp["infraRsSpinePGrpToLldpIfPol"]
            )
            builder.config.addMo(RsSpinePGrpToLldpIfPol)


@register("infraSpAccPortP")
def infra_sp_acc_port_p(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Interfaces > Spine Interfaces > Profiles."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    for infraSpAccPortP in value:
        SpAccPortP = cobra.model.infra.SpAccPortP(Infra, **infraSpAccPortP)
        builder.config.addMo(SpAccPortP)
        if "infraSHPortS" in infraSpAccPortP:
            for infraSHPortS in infraSpAccPortP["infraSHPortS"]:
                SHPortS = cobra.model.infra.SHPortS(SpAccPortP, **infraSHPortS)
                builder.config.addMo(SHPortS)
                if "infraRsSpAccGrp" in infraSHPortS:
                    RsSpAccGrp = cobra.model.infra.RsSpAccGrp(
                        SHPortS, **infraSHPortS["infraRsSpAccGrp"]
                    )
                    builder.config.addMo(RsSpAccGrp)
                if "infraPortBlk" in infraSHPortS:
                    for infraPortBlk in infraSHPortS["infraPortBlk"]:
                        PortBlk = cobra.model.infra.PortBlk(SHPortS, **infraPortBlk)
                        builder.config.addMo(PortBlk)


@register("infraSpAccPortGrp")
def infra_sp_acc_port_grp(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Interfaces > Spine Interfaces > Policy Groups."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    FuncP = cobra.model.infra.FuncP(Infra)
    for infraSpAccPortGrp in value:
        SpAccPortGrp = cobra.model.infra.SpAccPortGrp(FuncP, **infraSpAccPortGrp)
        builder.config.addMo(SpAccPortGrp)
        if "infraRsHIfPol" in infraSpAccPortGrp:
            RsHIfPol = cobra.model.infra.RsHIfPol(
                SpAccPortGrp, **infraSpAccPortGrp["infraRsHIfPol"]
            )
            builder.config.addMo(RsHIfPol)
        if "infraRsCdpIfPol" in infraSpAccPortGrp:
            RsCdpIfPol = cobra.model.infra.RsCdpIfPol(
                SpAccPortGrp, **infraSpAccPortGrp["infraRsCdpIfPol"]
            )
            builder.config.addMo(RsCdpIfPol)
        if "infraRsMacsecIfPol" in infraSpAccPortGrp:
            RsMacsecIfPol = cobra.model.infra.RsMacsecIfPol(
                SpAccPortGrp, **infraSpAccPortGrp["infraRsMacsecIfPol"]
            )
            builder.config.addMo(RsMacsecIfPol)
        if "infraRsAttEntP" in infraSpAccPortGrp:
            RsAttEntP = cobra.model.infra.RsAttEntP(
                SpAccPortGrp, **infraSpAccPortGrp["infraRsAttEntP"]
            )
            builder.config.addMo(RsAttEntP)
        if "infraRsLinkFlapPol" in infraSpAccPortGrp:
            RsLinkFlapPol = cobra.model.infra.RsLinkFlapPol(
                SpAccPortGrp, **infraSpAccPortGrp["infraRsLinkFlapPol"]
            )
            builder.config.addMo(RsLinkFlapPol)
        if "infraRsCoppIfPol" in infraSpAccPortGrp:
            RsCoppIfPol = cobra.model.infra.RsCoppIfPol(
                SpAccPortGrp, **infraSpAccPortGrp["infraRsCoppIfPol"]
            )
            builder.config.addMo(RsCoppIfPol)


@register("infraAccPortP")
def infra_acc_port_p(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Interfaces > Leaf Interfaces > Profiles."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    for infraAccPortP in value:
        AccPortP = cobra.model.infra.AccPortP(Infra, **infraAccPortP)
        builder.config.addMo(AccPortP)
        if "infraHPortS" in infraAccPortP:
            for infraHPortS in infraAccPortP["infraHPortS"]:
                HPortS = cobra.model.infra.HPortS(AccPortP, **infraHPortS)
                builder.config.addMo(HPortS)
                if "infraRsAccBaseGrp" in infraHPortS:
                    if not_nan_str(infraHPortS["infraRsAccBaseGrp"], ["tDn"]):
                        RsAccBaseGrp = cobra.model.infra.RsAccBaseGrp(
                            HPortS, **infraHPortS["infraRsAccBaseGrp"]
                        )
                        builder.config.addMo(RsAccBaseGrp)
                if "infraPortBlk" in infraHPortS:
                    for infraPortBlk in infraHPortS["infraPortBlk"]:
                        if not_nan_str(infraPortBlk, ["fromPort"]):
                            PortBlk = cobra.model.infra.PortBlk(HPortS, **infraPortBlk)
                            builder.config.addMo(PortBlk)


@register("infraFexP")
def infra_fex_p(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Interfaces > Leaf Interfaces > FEX Profiles."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    for infraFexP in value:
        FexP = cobra.model.infra.FexP(Infra, **infraFexP)
        builder.config.addMo(FexP)
        if "infraHPortS" in infraFexP:
            for infraHPortS in infraFexP["infraHPortS"]:
                HPortS = cobra.model.infra.HPortS(FexP, **infraHPortS)
                builder.config.addMo(HPortS)
                if "infraRsAccBaseGrp" in infraHPortS:
                    RsAccBaseGrp = cobra.model.infra.RsAccBaseGrp(
                        HPortS, **infraHPortS["infraRsAccBaseGrp"]
                    )
                    builder.config.addMo(RsAccBaseGrp)
                if "infraPortBlk" in infraHPortS:
                    for block in infraHPortS["infraPortBlk"]:
                        PortBlk = cobra.model.infra.PortBlk(HPortS, **block)
                        builder.config.addMo(PortBlk)
        if "infraFexBndlGrp" in infraFexP:
            FexBndlGrp = cobra.model.infra.FexBndlGrp(FexP, **infraFexP["infraFexBndlGrp"])
            builder.config.addMo(FexBndlGrp)


@register("infraAccPortGrp")
def infra_acc_port_grp(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Interfaces > Leaf Interfaces > Policy Groups > Access."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    FuncP = cobra.model.infra.FuncP(Infra)
    for infraAccPortGrp in value:
        AccPortGrp = cobra.model.infra.AccPortGrp(FuncP, **infraAccPortGrp)
        builder.config.addMo(AccPortGrp)
        if "infraRsAttEntP" in infraAccPortGrp:
            if not_nan_str(infraAccPortGrp["infraRsAttEntP"], ["tDn"]):
                RsAttEntP = cobra.model.infra.RsAttEntP(
                    AccPortGrp, **infraAccPortGrp["infraRsAttEntP"]
                )
                builder.config.addMo(RsAttEntP)
        if "infraRsStpIfPol" in infraAccPortGrp:
            if not_nan_str(infraAccPortGrp["infraRsStpIfPol"], ["tnStpIfPolName"]):
                RsStpIfPol = cobra.model.infra.RsStpIfPol(
                    AccPortGrp, **infraAccPortGrp["infraRsStpIfPol"]
                )
                builder.config.addMo(RsStpIfPol)
        if "infraRsQosLlfcIfPol" in infraAccPortGrp:
            if not_nan_str(infraAccPortGrp["infraRsQosLlfcIfPol"], ["tnQosLlfcIfPolName"]):
                RsQosLlfcIfPol = cobra.model.infra.RsQosLlfcIfPol(
                    AccPortGrp, **infraAccPortGrp["infraRsQosLlfcIfPol"]
                )
                builder.config.addMo(RsQosLlfcIfPol)
        if "infraRsQosIngressDppIfPol" in infraAccPortGrp:
            if not_nan_str(infraAccPortGrp["infraRsQosIngressDppIfPol"], ["tnQosDppPolName"]):
                RsQosIngressDppIfPol = cobra.model.infra.RsQosIngressDppIfPol(
                    AccPortGrp, **infraAccPortGrp["infraRsQosIngressDppIfPol"]
                )
                builder.config.addMo(RsQosIngressDppIfPol)
        if "infraRsStormctrlIfPol" in infraAccPortGrp:
            if not_nan_str(infraAccPortGrp["infraRsStormctrlIfPol"], ["tnStormctrlIfPolName"]):
                RsStormctrlIfPol = cobra.model.infra.RsStormctrlIfPol(
                    AccPortGrp, **infraAccPortGrp["infraRsStormctrlIfPol"]
                )
                builder.config.addMo(RsStormctrlIfPol)
        if "infraRsQosEgressDppIfPol" in infraAccPortGrp:
            if not_nan_str(infraAccPortGrp["infraRsQosEgressDppIfPol"], ["tnQosDppPolName"]):
                RsQosEgressDppIfPol = cobra.model.infra.RsQosEgressDppIfPol(
                    AccPortGrp, **infraAccPortGrp["infraRsQosEgressDppIfPol"]
                )
                builder.config.addMo(RsQosEgressDppIfPol)
        if "infraRsMonIfInfraPol" in infraAccPortGrp:
            if not_nan_str(infraAccPortGrp["infraRsMonIfInfraPol"], ["tnMonInfraPolName"]):
                RsMonIfInfraPol = cobra.model.infra.RsMonIfInfraPol(
                    AccPortGrp, **infraAccPortGrp["infraRsMonIfInfraPol"]
                )
                builder.config.addMo(RsMonIfInfraPol)
        if "infraRsMcpIfPol" in infraAccPortGrp:
            if not_nan_str(infraAccPortGrp["infraRsMcpIfPol"], ["tnMcpIfPolName"]):
                RsMcpIfPol = cobra.model.infra.RsMcpIfPol(
                    AccPortGrp, **infraAccPortGrp["infraRsMcpIfPol"]
                )
                builder.config.addMo(RsMcpIfPol)
        if "infraRsMacsecIfPol" in infraAccPortGrp:
            if not_nan_str(infraAccPortGrp["infraRsMacsecIfPol"], ["tnMacsecIfPolName"]):
                RsMacsecIfPol = cobra.model.infra.RsMacsecIfPol(
                    AccPortGrp, **infraAccPortGrp["infraRsMacsecIfPol"]
                )
                builder.config.addMo(RsMacsecIfPol)
        if "infraRsQosSdIfPol" in infraAccPortGrp:
            if not_nan_str(infraAccPortGrp["infraRsQosSdIfPol"], ["tnQosSdIfPolName"]):
                RsQosSdIfPol = cobra.model.infra.RsQosSdIfPol(
                    AccPortGrp, **infraAccPortGrp["infraRsQosSdIfPol"]
                )
                builder.config.addMo(RsQosSdIfPol)
        if "infraRsCdpIfPol" in infraAccPortGrp:
            if not_nan_str(infraAccPortGrp["infraRsCdpIfPol"], ["tnCdpIfPolName"]):
                RsCdpIfPol = cobra.model.infra.RsCdpIfPol(
                    AccPortGrp, **infraAccPortGrp["infraRsCdpIfPol"]
                )
                builder.config.addMo(RsCdpIfPol)
        if "infraRsL2IfPol" in infraAccPortGrp:
            if not_nan_str(infraAccPortGrp["infraRsL2IfPol"], ["tnL2IfPolName"]):
                RsL2IfPol = cobra.model.infra.RsL2IfPol(
                    AccPortGrp, **infraAccPortGrp["infraRsL2IfPol"]
                )
                builder.config.addMo(RsL2IfPol)
        if "infraRsQosDppIfPol" in infraAccPortGrp:
            if not_nan_str(infraAccPortGrp["infraRsQosDppIfPol"], ["tnQosDppPolName"]):
                RsQosDppIfPol = cobra.model.infra.RsQosDppIfPol(
                    AccPortGrp, **infraAccPortGrp["infraRsQosDppIfPol"]
                )
                builder.config.addMo(RsQosDppIfPol)
        if "infraRsCoppIfPol" in infraAccPortGrp:
            if not_nan_str(infraAccPortGrp["infraRsCoppIfPol"], ["tnCoppIfPolName"]):
                RsCoppIfPol = cobra.model.infra.RsCoppIfPol(
                    AccPortGrp, **infraAccPortGrp["infraRsCoppIfPol"]
                )
                builder.config.addMo(RsCoppIfPol)
        if "infraRsDwdmIfPol" in infraAccPortGrp:
            if not_nan_str(infraAccPortGrp["infraRsDwdmIfPol"], ["tnDwdmIfPolName"]):
                RsDwdmIfPol = cobra.model.infra.RsDwdmIfPol(
                    AccPortGrp, **infraAccPortGrp["infraRsDwdmIfPol"]
                )
                builder.config.addMo(RsDwdmIfPol)
        if "infraRsLinkFlapPol" in infraAccPortGrp:
            if not_nan_str(infraAccPortGrp["infraRsLinkFlapPol"], ["tnFabricLinkFlapPolName"]):
                RsLinkFlapPol = cobra.model.infra.RsLinkFlapPol(
                    AccPortGrp, **infraAccPortGrp["infraRsLinkFlapPol"]
                )
                builder.config.addMo(RsLinkFlapPol)
        if "infraRsLldpIfPol" in infraAccPortGrp:
            if not_nan_str(infraAccPortGrp["infraRsLldpIfPol"], ["tnLldpIfPolName"]):
                RsLldpIfPol = cobra.model.infra.RsLldpIfPol(
                    AccPortGrp, **infraAccPortGrp["infraRsLldpIfPol"]
                )
                builder.config.addMo(RsLldpIfPol)
        if "infraRsFcIfPol" in infraAccPortGrp:
            if not_nan_str(infraAccPortGrp["infraRsFcIfPol"], ["tnFcIfPolName"]):
                RsFcIfPol = cobra.model.infra.RsFcIfPol(
                    AccPortGrp, **infraAccPortGrp["infraRsFcIfPol"]
                )
                builder.config.addMo(RsFcIfPol)
        if "infraRsQosPfcIfPol" in infraAccPortGrp:
            if not_nan_str(infraAccPortGrp["infraRsQosPfcIfPol"], ["tnQosPfcIfPolName"]):
                RsQosPfcIfPol = cobra.model.infra.RsQosPfcIfPol(
                    AccPortGrp, **infraAccPortGrp["infraRsQosPfcIfPol"]
                )
                builder.config.addMo(RsQosPfcIfPol)
        if "infraRsHIfPol" in infraAccPortGrp:
            if not_nan_str(infraAccPortGrp["infraRsHIfPol"], ["tnFabricHIfPolName"]):
                RsHIfPol = cobra.model.infra.RsHIfPol(
                    AccPortGrp, **infraAccPortGrp["infraRsHIfPol"]
                )
                builder.config.addMo(RsHIfPol)
        if "infraRsL2PortSecurityPol" in infraAccPortGrp:
            if not_nan_str(
                infraAccPortGrp["infraRsL2PortSecurityPol"], ["tnL2PortSecurityPolName"]
            ):
                RsL2PortSecurityPol = cobra.model.infra.RsL2PortSecurityPol(
                    AccPortGrp, **infraAccPortGrp["infraRsL2PortSecurityPol"]
                )
                builder.config.addMo(RsL2PortSecurityPol)
        if "infraRsL2PortAuthPol" in infraAccPortGrp:
            if not_nan_str(infraAccPortGrp["infraRsL2PortAuthPol"], ["tnL2PortAuthPolName"]):
                RsL2PortAuthPol = cobra.model.infra.RsL2PortAuthPol(
                    AccPortGrp, **infraAccPortGrp["infraRsL2PortAuthPol"]
                )
                builder.config.addMo(RsL2PortAuthPol)


@register("infraAccBndlGrp")
def infra_acc_bndl_grp(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Interfaces > Leaf Interfaces > Policy Groups > PC or VPC."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    FuncP = cobra.model.infra.FuncP(Infra)
    for infraAccBndlGrp in value:
        AccBndlGrp = cobra.model.infra.AccBndlGrp(FuncP, **infraAccBndlGrp)
        builder.config.addMo(AccBndlGrp)
        if "infraRsAttEntP" in infraAccBndlGrp:
            if not_nan_str(infraAccBndlGrp["infraRsAttEntP"], ["tDn"]):
                RsAttEntP = cobra.model.infra.RsAttEntP(
                    AccBndlGrp, **infraAccBndlGrp["infraRsAttEntP"]
                )
                builder.config.addMo(RsAttEntP)
        if "infraRsStpIfPol" in infraAccBndlGrp:
            if not_nan_str(infraAccBndlGrp["infraRsStpIfPol"], ["tnStpIfPolName"]):
                RsStpIfPol = cobra.model.infra.RsStpIfPol(
                    AccBndlGrp, **infraAccBndlGrp["infraRsStpIfPol"]
                )
                builder.config.addMo(RsStpIfPol)
        if "infraRsQosLlfcIfPol" in infraAccBndlGrp:
            if not_nan_str(infraAccBndlGrp["infraRsQosLlfcIfPol"], ["tnQosLlfcIfPolName"]):
                RsQosLlfcIfPol = cobra.model.infra.RsQosLlfcIfPol(
                    AccBndlGrp, **infraAccBndlGrp["infraRsQosLlfcIfPol"]
                )
                builder.config.addMo(RsQosLlfcIfPol)
        if "infraRsQosIngressDppIfPol" in infraAccBndlGrp:
            if not_nan_str(infraAccBndlGrp["infraRsQosIngressDppIfPol"], ["tnQosDppPolName"]):
                RsQosIngressDppIfPol = cobra.model.infra.RsQosIngressDppIfPol(
                    AccBndlGrp, **infraAccBndlGrp["infraRsQosIngressDppIfPol"]
                )
                builder.config.addMo(RsQosIngressDppIfPol)
        if "infraRsStormctrlIfPol" in infraAccBndlGrp:
            if not_nan_str(infraAccBndlGrp["infraRsStormctrlIfPol"], ["tnStormctrlIfPolName"]):
                RsStormctrlIfPol = cobra.model.infra.RsStormctrlIfPol(
                    AccBndlGrp, **infraAccBndlGrp["infraRsStormctrlIfPol"]
                )
                builder.config.addMo(RsStormctrlIfPol)
        if "infraRsQosEgressDppIfPol" in infraAccBndlGrp:
            if not_nan_str(infraAccBndlGrp["infraRsQosEgressDppIfPol"], ["tnQosDppPolName"]):
                RsQosEgressDppIfPol = cobra.model.infra.RsQosEgressDppIfPol(
                    AccBndlGrp, **infraAccBndlGrp["infraRsQosEgressDppIfPol"]
                )
                builder.config.addMo(RsQosEgressDppIfPol)
        if "infraRsMonIfInfraPol" in infraAccBndlGrp:
            if not_nan_str(infraAccBndlGrp["infraRsMonIfInfraPol"], ["tnMonInfraPolName"]):
                RsMonIfInfraPol = cobra.model.infra.RsMonIfInfraPol(
                    AccBndlGrp, **infraAccBndlGrp["infraRsMonIfInfraPol"]
                )
                builder.config.addMo(RsMonIfInfraPol)
        if "infraRsMcpIfPol" in infraAccBndlGrp:
            if not_nan_str(infraAccBndlGrp["infraRsMcpIfPol"], ["tnMcpIfPolName"]):
                RsMcpIfPol = cobra.model.infra.RsMcpIfPol(
                    AccBndlGrp, **infraAccBndlGrp["infraRsMcpIfPol"]
                )
                builder.config.addMo(RsMcpIfPol)
        if "infraRsMacsecIfPol" in infraAccBndlGrp:
            if not_nan_str(infraAccBndlGrp["infraRsMacsecIfPol"], ["tnMacsecIfPolName"]):
                RsMacsecIfPol = cobra.model.infra.RsMacsecIfPol(
                    AccBndlGrp, **infraAccBndlGrp["infraRsMacsecIfPol"]
                )
                builder.config.addMo(RsMacsecIfPol)
        if "infraRsQosSdIfPol" in infraAccBndlGrp:
            if not_nan_str(infraAccBndlGrp["infraRsQosSdIfPol"], ["tnQosSdIfPolName"]):
                RsQosSdIfPol = cobra.model.infra.RsQosSdIfPol(
                    AccBndlGrp, **infraAccBndlGrp["infraRsQosSdIfPol"]
                )
                builder.config.addMo(RsQosSdIfPol)
        if "infraRsCdpIfPol" in infraAccBndlGrp:
            if not_nan_str(infraAccBndlGrp["infraRsCdpIfPol"], ["tnCdpIfPolName"]):
                RsCdpIfPol = cobra.model.infra.RsCdpIfPol(
                    AccBndlGrp, **infraAccBndlGrp["infraRsCdpIfPol"]
                )
                builder.config.addMo(RsCdpIfPol)
        if "infraRsL2IfPol" in infraAccBndlGrp:
            if not_nan_str(infraAccBndlGrp["infraRsL2IfPol"], ["tnL2IfPolName"]):
                RsL2IfPol = cobra.model.infra.RsL2IfPol(
                    AccBndlGrp, **infraAccBndlGrp["infraRsL2IfPol"]
                )
                builder.config.addMo(RsL2IfPol)
        if "infraRsQosDppIfPol" in infraAccBndlGrp:
            if not_nan_str(infraAccBndlGrp["infraRsQosDppIfPol"], ["tnQosDppPolName"]):
                RsQosDppIfPol = cobra.model.infra.RsQosDppIfPol(
                    AccBndlGrp, **infraAccBndlGrp["infraRsQosDppIfPol"]
                )
                builder.config.addMo(RsQosDppIfPol)
        if "infraRsCoppIfPol" in infraAccBndlGrp:
            if not_nan_str(infraAccBndlGrp["infraRsCoppIfPol"], ["tnCoppIfPolName"]):
                RsCoppIfPol = cobra.model.infra.RsCoppIfPol(
                    AccBndlGrp, **infraAccBndlGrp["infraRsCoppIfPol"]
                )
                builder.config.addMo(RsCoppIfPol)
        if "infraRsLldpIfPol" in infraAccBndlGrp:
            if not_nan_str(infraAccBndlGrp["infraRsLldpIfPol"], ["tnLldpIfPolName"]):
                RsLldpIfPol = cobra.model.infra.RsLldpIfPol(
                    AccBndlGrp, **infraAccBndlGrp["infraRsLldpIfPol"]
                )
                builder.config.addMo(RsLldpIfPol)
        if "infraRsFcIfPol" in infraAccBndlGrp:
            if not_nan_str(infraAccBndlGrp["infraRsFcIfPol"], ["tnFcIfPolName"]):
                RsFcIfPol = cobra.model.infra.RsFcIfPol(
                    AccBndlGrp, **infraAccBndlGrp["infraRsFcIfPol"]
                )
                builder.config.addMo(RsFcIfPol)
        if "infraRsQosPfcIfPol" in infraAccBndlGrp:
            if not_nan_str(infraAccBndlGrp["infraRsQosPfcIfPol"], ["tnQosPfcIfPolName"]):
                RsQosPfcIfPol = cobra.model.infra.RsQosPfcIfPol(
                    AccBndlGrp, **infraAccBndlGrp["infraRsQosPfcIfPol"]
                )
                builder.config.addMo(RsQosPfcIfPol)
        if "infraRsHIfPol" in infraAccBndlGrp:
            if not_nan_str(infraAccBndlGrp["infraRsHIfPol"], ["tnFabricHIfPolName"]):
                RsHIfPol = cobra.model.infra.RsHIfPol(
                    AccBndlGrp, **infraAccBndlGrp["infraRsHIfPol"]
                )
                builder.config.addMo(RsHIfPol)
        if "infraRsL2PortSecurityPol" in infraAccBndlGrp:
            if not_nan_str(
                infraAccBndlGrp["infraRsL2PortSecurityPol"], ["tnL2PortSecurityPolName"]
            ):
                RsL2PortSecurityPol = cobra.model.infra.RsL2PortSecurityPol(
                    AccBndlGrp, **infraAccBndlGrp["infraRsL2PortSecurityPol"]
                )
                builder.config.addMo(RsL2PortSecurityPol)
        if "infraRsL2PortAuthPol" in infraAccBndlGrp:
            if not_nan_str(infraAccBndlGrp["infraRsL2PortAuthPol"], ["tnL2PortAuthPolName"]):
                RsL2PortAuthPol = cobra.model.infra.RsL2PortAuthPol(
                    AccBndlGrp, **infraAccBndlGrp["infraRsL2PortAuthPol"]
                )
                builder.config.addMo(RsL2PortAuthPol)
        if "infraRsLacpPol" in infraAccBndlGrp:
            if not_nan_str(infraAccBndlGrp["infraRsLacpPol"], ["tnLacpLagPolName"]):
                RsLacpPol = cobra.model.infra.RsLacpPol(
                    AccBndlGrp, **infraAccBndlGrp["infraRsLacpPol"]
                )
                builder.config.addMo(RsLacpPol)
        if "infraRsLinkFlapPol" in infraAccBndlGrp:
            if not_nan_str(infraAccBndlGrp["infraRsLinkFlapPol"], ["tnFabricLinkFlapPolName"]):
                RsLinkFlapPol = cobra.model.infra.RsLinkFlapPol(
                    AccBndlGrp, **infraAccBndlGrp["infraRsLinkFlapPol"]
                )
                builder.config.addMo(RsLinkFlapPol)


@register("infraAttEntityP")
def infra_att_entity_p(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Policies > Global > Attachable Access Entity Profiles."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    for infraAttEntityP in value:
        AttEntityP = cobra.model.infra.AttEntityP(Infra, **infraAttEntityP)
        builder.config.addMo(AttEntityP)
        if "infraRsDomP" in infraAttEntityP:
            for infraRsDomP in infraAttEntityP["infraRsDomP"]:
                RsDomP = cobra.model.infra.RsDomP(AttEntityP, **infraRsDomP)
                builder.config.addMo(RsDomP)


@register("fvnsVlanInstP")
def fvns_vlan_inst_p(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Pools > VLAN."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    for fvnsVlanInstP in value:
        VlanInstP = cobra.model.fvns.VlanInstP(Infra, **fvnsVlanInstP)
        builder.config.addMo(VlanInstP)
        if "fvnsEncapBlk" in fvnsVlanInstP:
            for fvnsEncapBlk in fvnsVlanInstP["fvnsEncapBlk"]:
                EncapBlk = cobra.model.fvns.EncapBlk(VlanInstP, **fvnsEncapBlk)
                builder.config.addMo(EncapBlk)


@register("physDomP")
def phys_dom_p(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Physical and External Domains > Physical Domain."""
    Uni = cobra.model.pol.Uni(builder.root)
    for physDomP in value:
        DomP = cobra.model.phys.DomP(Uni, **physDomP)
        builder.config.addMo(DomP)
        if "infraRsVlanNs" in physDomP:
            RsVlanNs = cobra.model.infra.RsVlanNs(DomP, **physDomP["infraRsVlanNs"])
            builder.config.addMo(RsVlanNs)


@register("l3extDomP")
def l3ext_dom_p(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Physical and External Domains > L3 Domains."""
    Uni = cobra.model.pol.Uni(builder.root)
    for l3extDomP in value:
        DomP = cobra.model.l3ext.DomP(Uni, **l3extDomP)
        builder.config.addMo(DomP)
        if "infraRsVlanNs" in l3extDomP:
            RsVlanNs = cobra.model.infra.RsVlanNs(DomP, **l3extDomP["infraRsVlanNs"])
            builder.config.addMo(RsVlanNs)


@register("l2extDomP")
def l2ext_dom_p(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Physical and External Domains > External Bridged Domains."""
    Uni = cobra.model.pol.Uni(builder.root)
    for l2extDomP in value:
        DomP = cobra.model.l2ext.DomP(Uni, **l2extDomP)
        builder.config.addMo(DomP)
        if "infraRsVlanNs" in l2extDomP:
            RsVlanNs = cobra.model.infra.RsVlanNs(DomP, **l2extDomP["infraRsVlanNs"])
            builder.config.addMo(RsVlanNs)


# --------------------------------------------------------------------------- Policies


@register("fabricProtPol")
def fabric_prot_pol(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Policies > Switch > Virtual Port Channel default."""
    Uni = cobra.model.pol.Uni(builder.root)
    Inst = cobra.model.fabric.Inst(Uni)
    for fabricProtPol in value:
        ProtPol = cobra.model.fabric.ProtPol(Inst, **fabricProtPol)
        builder.config.addMo(ProtPol)
        if "fabricExplicitGEp" in fabricProtPol:
            for fabricExplicitGEp in fabricProtPol["fabricExplicitGEp"]:
                ExplicitGEp = cobra.model.fabric.ExplicitGEp(ProtPol, **fabricExplicitGEp)
                builder.config.addMo(ExplicitGEp)
                if "fabricRsVpcInstPol" in fabricExplicitGEp:
                    RsVpcInstPol = cobra.model.fabric.RsVpcInstPol(
                        ExplicitGEp, **fabricExplicitGEp["fabricRsVpcInstPol"]
                    )
                    builder.config.addMo(RsVpcInstPol)
                if "fabricNodePEp" in fabricExplicitGEp:
                    for fabricNodePEp in fabricExplicitGEp["fabricNodePEp"]:
                        NodePEp = cobra.model.fabric.NodePEp(ExplicitGEp, **fabricNodePEp)
                        builder.config.addMo(NodePEp)


@register("fabricHIfPol")
def fabric_h_if_pol(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Policies > Interface > Link Level."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    for fabricHIfPol in value:
        HIfPol = cobra.model.fabric.HIfPol(Infra, **fabricHIfPol)
        builder.config.addMo(HIfPol)


@register("qosPfcIfPol")
def qos_pfc_if_pol(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Policies > Interface > Priority Flow Control."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    for qosPfcIfPol in value:
        PfcIfPol = cobra.model.qos.PfcIfPol(Infra, **qosPfcIfPol)
        builder.config.addMo(PfcIfPol)


@register("cdpIfPol")
def cdp_if_pol(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Policies > Interface > CDP Interface."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    for cdpIfPol in value:
        IfPol = cobra.model.cdp.IfPol(Infra, **cdpIfPol)
        builder.config.addMo(IfPol)


@register("lldpIfPol")
def lldp_if_pol(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Policies > Interface > LLDP Interface."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    for lldpIfPol in value:
        IfPol = cobra.model.lldp.IfPol(Infra, **lldpIfPol)
        builder.config.addMo(IfPol)


@register("lacpLagPol")
def lacp_lag_pol(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Policies > Interface > Port Channel."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    for lacpLagPol in value:
        LagPol = cobra.model.lacp.LagPol(Infra, **lacpLagPol)
        builder.config.addMo(LagPol)


@register("stpIfPol")
def stp_if_pol(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Policies > Interface > Spanning Tree Interface."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    for stpIfPol in value:
        IfPol = cobra.model.stp.IfPol(Infra, **stpIfPol)
        builder.config.addMo(IfPol)


@register("stormctrlIfPol")
def stormctrl_if_pol(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Policies > Interface > Storm Control."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    for stormctrlIfPol in value:
        IfPol = cobra.model.stormctrl.IfPol(Infra, **stormctrlIfPol)
        builder.config.addMo(IfPol)


@register("mcpIfPol")
def mcp_if_pol(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Policies > Interface > MCP Interface."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    for mcpIfPol in value:
        IfPol = cobra.model.mcp.IfPol(Infra, **mcpIfPol)
        builder.config.addMo(IfPol)


@register("bgpInstPol")
def bgp_inst_pol(builder: CobraBuilder, value: Any) -> None:
    """System Settings > All Tenants."""
    Inst = cobra.model.fabric.Inst(builder.uni)
    for bgpInstPol in value:
        InstPol = cobra.model.bgp.InstPol(Inst, **bgpInstPol)
        builder.config.addMo(InstPol)
        if "bgpAsP" in bgpInstPol:
            if not_nan_str(bgpInstPol["bgpAsP"], ["asn"]):
                AsP = cobra.model.bgp.AsP(InstPol, **bgpInstPol["bgpAsP"])
                builder.config.addMo(AsP)
        if "bgpRRP" in bgpInstPol:
            RRP = cobra.model.bgp.RRP(InstPol)
            builder.config.addMo(RRP)
            for bgpRRP in bgpInstPol["bgpRRP"]:
                if "bgpRRNodePEp" in bgpRRP:
                    RRNodePEp = cobra.model.bgp.RRNodePEp(RRP, **bgpRRP["bgpRRNodePEp"])
                    builder.config.addMo(RRNodePEp)
        if "ExtRRP" in bgpInstPol:
            ExtRRP = cobra.model.bgp.ExtRRP(InstPol)
            for extRRP in bgpInstPol["ExtRRP"]:
                RRNodePEp = cobra.model.bgp.RRNodePEp(ExtRRP, **extRRP)
                builder.config.addMo(RRNodePEp)


@register("coopPol")
def coop_pol(builder: CobraBuilder, value: Any) -> None:
    """System Settings > COOP Group."""
    Inst = cobra.model.fabric.Inst(builder.uni)
    for coopPol in value:
        Pol = cobra.model.coop.Pol(Inst, **coopPol)
        builder.config.addMo(Pol)


@register("datetimeFormat")
def datetime_format(builder: CobraBuilder, value: Any) -> None:
    """System Settings > Date and Time."""
    Inst = cobra.model.fabric.Inst(builder.uni)
    for datetimeFormat in value:
        Format = cobra.model.datetime.Format(Inst, **datetimeFormat)
        builder.config.addMo(Format)


@register("aaaFabricSec")
def aaa_fabric_sec(builder: CobraBuilder, value: Any) -> None:
    """System Settings > Fabric Security."""
    UserEp = cobra.model.aaa.UserEp(builder.uni)
    for aaaFabricSec in value:
        FabricSec = cobra.model.aaa.FabricSec(UserEp, **aaaFabricSec)
        builder.config.addMo(FabricSec)


@register("aaaPreLoginBanner")
def aaa_pre_login_banner(builder: CobraBuilder, value: Any) -> None:
    """System Settings > System Alias and Banners."""
    UserEp = cobra.model.aaa.UserEp(builder.uni)
    for aaaPreLoginBanner in value:
        PreLoginBanner = cobra.model.aaa.PreLoginBanner(UserEp, **aaaPreLoginBanner)
        builder.config.addMo(PreLoginBanner)


@register("pkiExportEncryptionKey")
def pki_export_encryption_key(builder: CobraBuilder, value: Any) -> None:
    """System Settings > Fabric Security."""
    for pkiExportEncryptionKey in value:
        ExportEncryptionKey = cobra.model.pki.ExportEncryptionKey(
            builder.uni, **pkiExportEncryptionKey
        )
        builder.config.addMo(ExportEncryptionKey)


@register("epLoopProtectP")
def ep_loop_protect_p(builder: CobraBuilder, value: Any) -> None:
    """System Settings > Enpoint Controls > The endpoint loop protection."""
    Infra = cobra.model.infra.Infra(builder.uni)
    for epLoopProtectP in value:
        LoopProtectP = cobra.model.ep.LoopProtectP(Infra, **epLoopProtectP)
        builder.config.addMo(LoopProtectP)


@register("epControlP")
def ep_control_p(builder: CobraBuilder, value: Any) -> None:
    """System Settings > Enpoint Controls > Rogue EP Control."""
    Infra = cobra.model.infra.Infra(builder.uni)
    for epControlP in value:
        ControlP = cobra.model.ep.ControlP(Infra, **epControlP)
        builder.config.addMo(ControlP)


@register("epIpAgingP")
def ep_ip_aging_p(builder: CobraBuilder, value: Any) -> None:
    """System Settings > Enpoint Controls > IP Aging."""
    Infra = cobra.model.infra.Infra(builder.uni)
    for epIpAgingP in value:
        IpAgingP = cobra.model.ep.IpAgingP(Infra, **epIpAgingP)
        builder.config.addMo(IpAgingP)


@register("infraSetPol")
def infra_set_pol(builder: CobraBuilder, value: Any) -> None:
    """System Settings > Fabric-Wide Settings."""
    Infra = cobra.model.infra.Infra(builder.uni)
    for infraSetPol in value:
        SetPol = cobra.model.infra.SetPol(Infra, **infraSetPol)
        builder.config.addMo(SetPol)


@register("isisDomPol")
def isis_dom_pol(builder: CobraBuilder, value: Any) -> None:
    """System Settings > ISIS Policy."""
    Inst = cobra.model.fabric.Inst(builder.uni)
    for isisDomPol in value:
        DomPol = cobra.model.isis.DomPol(Inst, **isisDomPol)
        builder.config.addMo(DomPol)


@register("infraPortTrackPol")
def infra_port_track_pol(builder: CobraBuilder, value: Any) -> None:
    """System Settings > Port Tracking."""
    Infra = cobra.model.infra.Infra(builder.uni)
    for infraPortTrackPol in value:
        PortTrackPol = cobra.model.infra.PortTrackPol(Infra, **infraPortTrackPol)
        builder.config.addMo(PortTrackPol)


@register("mcpInstPol")
def mcp_inst_pol(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Global > MCP Instance Policy default."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    for mcpInstPol in value:
        InstPol = cobra.model.mcp.InstPol(Infra, **mcpInstPol)
        builder.config.addMo(InstPol)


@register("fabricNodeControl")
def fabric_node_control(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Fabric Policies > Policies > Monitoring > Fabric Node Controls > default."""
    Uni = cobra.model.pol.Uni(builder.root)
    Inst = cobra.model.fabric.Inst(Uni)
    for fabricNodeControl in value:
        NodeControl = cobra.model.fabric.NodeControl(Inst, **fabricNodeControl)
        builder.config.addMo(NodeControl)


@register("geoSite")
def geo_site(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Fabric Policies > Policies > Geolocation."""
    Uni = cobra.model.pol.Uni(builder.root)
    Inst = cobra.model.fabric.Inst(Uni)
    for geoSite in value:
        Site = cobra.model.geo.Site(Inst, **geoSite)
        builder.config.addMo(Site)
        if "geoBuilding" in geoSite:
            for geoBuilding in geoSite["geoBuilding"]:
                Building = cobra.model.geo.Building(Site, **geoBuilding)
                builder.config.addMo(Building)
                if "geoFloor" in geoBuilding:
                    for geoFloor in geoBuilding["geoFloor"]:
                        Floor = cobra.model.geo.Floor(Building, **geoFloor)
                        builder.config.addMo(Floor)
                        if "geoRoom" in geoFloor:
                            for geoRoom in geoFloor["geoRoom"]:
                                Room = cobra.model.geo.Room(Floor, **geoRoom)
                                builder.config.addMo(Room)
                                if "geoRow" in geoRoom:
                                    for geoRow in geoRoom["geoRow"]:
                                        Row = cobra.model.geo.Row(Room, **geoRow)
                                        builder.config.addMo(Row)
                                        if "geoRack" in geoRow:
                                            for geoRack in geoRow["geoRack"]:
                                                if not_nan_str(geoRack, ["name"]):
                                                    Rack = cobra.model.geo.Rack(Row, **geoRack)
                                                    builder.config.addMo(Rack)
                                                    if "geoRsNodeLocation" in geoRack:
                                                        for loc in geoRack["geoRsNodeLocation"]:
                                                            if not_nan_str(loc, ["tDn"]):
                                                                RsNodeLocation = (
                                                                    cobra.model.geo.RsNodeLocation(
                                                                        Rack, **loc
                                                                    )
                                                                )
                                                                builder.config.addMo(RsNodeLocation)


@register("latencyPtpMode")
def latency_ptp_mode(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Fabric Policies > Policies > Monitoring > Fabric Node Controls > default."""
    Inst = cobra.model.fabric.Inst(builder.uni)
    for latencyPtpMode in value:
        PtpMode = cobra.model.latency.PtpMode(Inst, **latencyPtpMode)
        builder.config.addMo(PtpMode)


@register("infrazoneZoneP")
def infrazone_zone_p(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Fabric Policies > Policies > Monitoring > Fabric Node Controls > default."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    ZoneP = cobra.model.infrazone.ZoneP(Infra, **value)
    builder.config.addMo(ZoneP)
    for infrazoneZone in value:
        if "Zone" in infrazoneZone:
            Zone = cobra.model.infrazone.Zone(ZoneP, **infrazoneZone["Zone"])
            builder.config.addMo(Zone)
