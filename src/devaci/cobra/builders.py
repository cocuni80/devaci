"""Cobra object builders, grouped by ACI domain.

Each handler is registered under the top-level YAML/template key it handles.
Local variables keep the PascalCase style of the Cobra SDK to mirror the
managed-object class names.
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

from devaci.cobra.base import Handler, not_nan_str

if TYPE_CHECKING:
    from devaci.cobra import CobraBuilder


# --------------------------------------------------------------------------- Tenant


def fv_tenant(builder: CobraBuilder, value: Any) -> None:
    """Tenants > All Tenants."""
    Uni = cobra.model.pol.Uni(builder.root)
    for fvTenant in value:
        builder.add(cobra.model.fv.Tenant(Uni, **fvTenant))


def fv_ap(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Application Profiles."""
    Uni = cobra.model.pol.Uni(builder.root)
    for fvAp in value:
        if not_nan_str(fvAp, ["name", "tenant"]):
            Tenant = cobra.model.fv.Tenant(Uni, name=fvAp["tenant"])
            Ap = cobra.model.fv.Ap(Tenant, **fvAp)
            builder.add(Ap)


def fv_aepg(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Application Profiles > Application EPGs."""
    Uni = cobra.model.pol.Uni(builder.root)
    for fvAEPg in value:
        Tenant = cobra.model.fv.Tenant(Uni, name=fvAEPg["tenant"])
        Ap = cobra.model.fv.Ap(Tenant, name=fvAEPg["fvApName"])
        AEPg = cobra.model.fv.AEPg(Ap, **fvAEPg)
        builder.add(AEPg)
        if "fvRsBd" in fvAEPg:
            if not_nan_str(fvAEPg["fvRsBd"], ["tnFvBDName"]):
                RsBd = cobra.model.fv.RsBd(AEPg, **fvAEPg["fvRsBd"])
                builder.add(RsBd)
        if "fvRsDomAtt" in fvAEPg:
            for fvRsDomAtt in fvAEPg["fvRsDomAtt"]:
                if not_nan_str(fvRsDomAtt, ["tDn"]):
                    RsDomAtt = cobra.model.fv.RsDomAtt(AEPg, **fvRsDomAtt)
                    builder.add(RsDomAtt)
        if "fvRsPathAtt" in fvAEPg:
            for fvRsPathAtt in fvAEPg["fvRsPathAtt"]:
                if not_nan_str(fvRsPathAtt, ["tDn", "primaryEncap", "mode"]):
                    RsPathAtt = cobra.model.fv.RsPathAtt(AEPg, **fvRsPathAtt)
                    builder.add(RsPathAtt)


def static_path(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Application Profiles > Application EPGs > EPG Name > Static Ports."""
    Uni = cobra.model.pol.Uni(builder.root)
    for fvAp in value:
        Tenant = cobra.model.fv.Tenant(Uni, name=fvAp["tenant"])
        builder.add(Tenant)
        Ap = cobra.model.fv.Ap(Tenant, **fvAp)
        builder.add(Ap)
        if "fvAEPg" in fvAp:
            for fvAEPg in fvAp["fvAEPg"]:
                AEPg = cobra.model.fv.AEPg(Ap, **fvAEPg)
                if "fvRsPathAtt" in fvAEPg:
                    for fvRsPathAtt in fvAEPg["fvRsPathAtt"]:
                        RsPathAtt = cobra.model.fv.RsPathAtt(AEPg, **fvRsPathAtt)
                        builder.add(RsPathAtt)


def fv_rs_path_att(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Application Profiles > Application EPGs > EPG Name > Static Ports."""
    Uni = cobra.model.pol.Uni(builder.root)
    for fvRsPathAtt in value:
        if not_nan_str(
            fvRsPathAtt, ["tenant", "fvApName", "fvAEPgName", "tDn", "primaryEncap", "mode"]
        ):
            Tenant = cobra.model.fv.Tenant(Uni, name=fvRsPathAtt["tenant"])
            builder.add(Tenant)
            Ap = cobra.model.fv.Ap(Tenant, name=fvRsPathAtt["fvApName"])
            builder.add(Ap)
            AEPg = cobra.model.fv.AEPg(Ap, name=fvRsPathAtt["fvAEPgName"])
            builder.add(AEPg)
            RsPathAtt = cobra.model.fv.RsPathAtt(AEPg, **fvRsPathAtt)
            builder.add(RsPathAtt)


def tenant_application_uepg(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Application Profiles > uSeg EPGs."""
    for item in value:
        mo = item
        builder.add(mo)


def tenant_application_esg(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Application Profiles > Endpoint Security Groups. TODO: implement."""
    pass


def fv_bd(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Networking > Bridge Domains."""
    Uni = cobra.model.pol.Uni(builder.root)
    for fvBD in value:
        Tenant = cobra.model.fv.Tenant(Uni, name=fvBD["tenant"])
        BD = cobra.model.fv.BD(Tenant, **fvBD)
        builder.add(BD)
        if "fvRsCtx" in fvBD:
            if not_nan_str(fvBD["fvRsCtx"], ["tnFvCtxName"]):
                RsCtx = cobra.model.fv.RsCtx(BD, **fvBD["fvRsCtx"])
                builder.add(RsCtx)
        if "igmpIfP" in fvBD:
            if not_nan_str(fvBD["igmpIfP"], ["name"]):
                IfP = cobra.model.igmp.IfP(BD, **fvBD["igmpIfP"])
                builder.add(IfP)
        if "fvRsBdToEpRet" in fvBD:
            if not_nan_str(fvBD["fvRsBdToEpRet"], ["tnFvEpRetPolName"]):
                RsBdToEpRet = cobra.model.fv.RsBdToEpRet(BD, **fvBD["fvRsBdToEpRet"])
                builder.add(RsBdToEpRet)
        if "fvRsIgmpsn" in fvBD:
            if not_nan_str(fvBD["fvRsIgmpsn"], ["tnIgmpSnoopPolName"]):
                RsIgmpsn = cobra.model.fv.RsIgmpsn(BD, **fvBD["fvRsIgmpsn"])
                builder.add(RsIgmpsn)
        if "fvRsMldsn" in fvBD:
            if not_nan_str(fvBD["fvRsMldsn"], ["tnMldSnoopPolName"]):
                RsMldsn = cobra.model.fv.RsMldsn(BD, **fvBD["fvRsMldsn"])
                builder.add(RsMldsn)
        if "fvRsBDToOut" in fvBD:
            if not_nan_str(fvBD["fvRsBDToOut"], ["tnL3extOutName"]):
                RsBDToOut = cobra.model.fv.RsBDToOut(BD, **fvBD["fvRsBDToOut"])
                builder.add(RsBDToOut)
        if "fvSubnet" in fvBD:
            for fvSubnet in fvBD["fvSubnet"]:
                if not_nan_str(fvSubnet, ["ip"]):
                    Subnet = cobra.model.fv.Subnet(BD, **fvSubnet)
                    builder.add(Subnet)


def fv_ctx(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Networking > VRFs."""
    Uni = cobra.model.pol.Uni(builder.root)
    for fvCtx in value:
        Tenant = cobra.model.fv.Tenant(Uni, name=fvCtx["tenant"])
        Ctx = cobra.model.fv.Ctx(Tenant, **fvCtx)
        builder.add(Ctx)
        if "vzAny" in fvCtx:
            Any = cobra.model.vz.Any(Ctx, **fvCtx["vzAny"])
            builder.add(Any)
            if "vzRsAnyToProv" in fvCtx["vzAny"]:
                for vzRsAnyToProv in fvCtx["vzAny"]["vzRsAnyToProv"]:
                    if not_nan_str(vzRsAnyToProv, ["tnVzBrCPName"]):
                        RsAnyToProv = cobra.model.vz.RsAnyToProv(Any, **vzRsAnyToProv)
                        builder.add(RsAnyToProv)
            if "vzRsAnyToCons" in fvCtx["vzAny"]:
                for vzRsAnyToCons in fvCtx["vzAny"]["vzRsAnyToCons"]:
                    if not_nan_str(vzRsAnyToCons, ["tnVzBrCPName"]):
                        RsAnyToCons = cobra.model.vz.RsAnyToCons(Any, **vzRsAnyToCons)
                        builder.add(RsAnyToCons)
        if "fvRsCtxToEpRet" in fvCtx:
            if not_nan_str(fvCtx["fvRsCtxToEpRet"], ["tnFvEpRetPolName"]):
                RsCtxToEpRet = cobra.model.fv.RsCtxToEpRet(Ctx, **fvCtx["fvRsCtxToEpRet"])
                builder.add(RsCtxToEpRet)
        if "fvRsCtxToExtRouteTagPol" in fvCtx:
            if not_nan_str(fvCtx["fvRsCtxToExtRouteTagPol"], ["tnL3extRouteTagPolName"]):
                RsCtxToExtRouteTagPol = cobra.model.fv.RsCtxToExtRouteTagPol(
                    Ctx, **fvCtx["fvRsCtxToExtRouteTagPol"]
                )
                builder.add(RsCtxToExtRouteTagPol)
        if "fvRsOspfCtxPol" in fvCtx:
            if not_nan_str(fvCtx["fvRsOspfCtxPol"], ["tnOspfCtxPolName"]):
                RsOspfCtxPol = cobra.model.fv.RsOspfCtxPol(Ctx, **fvCtx["fvRsOspfCtxPol"])
                builder.add(RsOspfCtxPol)
        if "fvRsBgpCtxPol" in fvCtx:
            if not_nan_str(fvCtx["fvRsBgpCtxPol"], ["tnBgpCtxPolName"]):
                RsBgpCtxPol = cobra.model.fv.RsBgpCtxPol(Ctx, **fvCtx["fvRsBgpCtxPol"])
                builder.add(RsBgpCtxPol)
        if "fvRsVrfValidationPol" in fvCtx:
            if not_nan_str(fvCtx["fvRsVrfValidationPol"], ["tnL3extVrfValidationPolName"]):
                RsVrfValidationPol = cobra.model.fv.RsVrfValidationPol(
                    Ctx, **fvCtx["fvRsVrfValidationPol"]
                )
                builder.add(RsVrfValidationPol)
        if "pimCtxP" in fvCtx:
            if not_nan_str(fvCtx["pimCtxP"], ["mtu"]):
                CtxP = cobra.model.pim.CtxP(Ctx, **fvCtx["pimCtxP"])
                builder.add(CtxP)


def tenant_network_l2out(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Networking > L2Outs. TODO: implement."""
    pass


def l3ext_out(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Networking > L3Outs. TODO: implement."""
    pass


def tenant_network_srmpls_l3out(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Networking > SR-MPLS VRF L3Outs. TODO: implement."""
    pass


def tenant_dot1q_tunnel(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Networking > Dot1Q Tunnels. TODO: implement."""
    pass


def fvns_addr_inst(builder: CobraBuilder, value: Any) -> None:
    """Tenants > mgmt > IP Address Pools."""
    Uni = cobra.model.pol.Uni(builder.root)
    for fvnsAddrInst in value:
        Tenant = cobra.model.fv.Tenant(Uni, name=fvnsAddrInst["tenant"])
        AddrInst = cobra.model.fvns.AddrInst(Tenant, **fvnsAddrInst)
        builder.add(AddrInst)
        if "fvnsUcastAddrBlk" in fvnsAddrInst:
            for fvnsUcastAddrBlk in fvnsAddrInst["fvnsUcastAddrBlk"]:
                if not_nan_str(fvnsUcastAddrBlk, ["from"]):
                    UcastAddrBlk = cobra.model.fvns.UcastAddrBlk(AddrInst, **fvnsUcastAddrBlk)
                    builder.add(UcastAddrBlk)


def mgmt_grp(builder: CobraBuilder, value: Any) -> None:
    """Tenants > mgmt > Managed Node Connectivity Groups."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    FuncP = cobra.model.infra.FuncP(Infra)
    for mgmtGrp in value:
        Grp = cobra.model.mgmt.Grp(FuncP, **mgmtGrp)
        builder.add(Grp)
        if "mgmtOoBZone" in mgmtGrp:
            OoBZone = cobra.model.mgmt.OoBZone(Grp)
            if "mgmtRsOoB" in mgmtGrp["mgmtOoBZone"]:
                RsOoB = cobra.model.mgmt.RsOoB(OoBZone, **mgmtGrp["mgmtOoBZone"]["mgmtRsOoB"])
                builder.add(RsOoB)
            if "mgmtRsAddrInst" in mgmtGrp["mgmtOoBZone"]:
                RsAddrInst = cobra.model.mgmt.RsAddrInst(
                    OoBZone, **mgmtGrp["mgmtOoBZone"]["mgmtRsAddrInst"]
                )
                builder.add(RsAddrInst)
        if "mgmtInBZone" in mgmtGrp:
            InBZone = cobra.model.mgmt.InBZone(Grp)
            if "mgmtRsInB" in mgmtGrp["mgmtInBZone"]:
                RsInB = cobra.model.mgmt.RsInB(InBZone, **mgmtGrp["mgmtInBZone"]["mgmtRsInB"])
                builder.add(RsInB)
            if "mgmtRsAddrInst" in mgmtGrp["mgmtInBZone"]:
                RsAddrInst = cobra.model.mgmt.RsAddrInst(
                    InBZone, **mgmtGrp["mgmtInBZone"]["mgmtRsAddrInst"]
                )
                builder.add(RsAddrInst)


def mgmt_node_grp(builder: CobraBuilder, value: Any) -> None:
    """Tenants > mgmt > Node Management Addresses."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    for mgmtNodeGrp in value:
        NodeGrp = cobra.model.mgmt.NodeGrp(Infra, **mgmtNodeGrp)
        builder.add(NodeGrp)
        if "mgmtRsGrp" in mgmtNodeGrp:
            for mgmtRsGrp in mgmtNodeGrp["mgmtRsGrp"]:
                RsGrp = cobra.model.mgmt.RsGrp(NodeGrp, **mgmtRsGrp)
                builder.add(RsGrp)
        if "infraNodeBlk" in mgmtNodeGrp:
            for infraNodeBlk in mgmtNodeGrp["infraNodeBlk"]:
                if not_nan_str(infraNodeBlk, ["from_"]):
                    NodeBlk = cobra.model.infra.NodeBlk(NodeGrp, **infraNodeBlk)
                    builder.add(NodeBlk)


def tenant_contract_standard(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Contracts > Standard. TODO: implement."""
    pass


def tenant_contract_taboo(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Contracts > Taboos. TODO: implement."""
    pass


def tenant_contract_imported(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Contracts > Imported. TODO: implement."""
    pass


def tenant_contract_filter(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Contracts > Filters. TODO: implement."""
    pass


def tenant_contract_oob(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Contracts > Out-Of-Band Contracts. TODO: implement."""
    pass


def tenant_policy_protocol_bfd(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Protocol > BFD. TODO: implement."""
    pass


def tenant_policy_protocol_bgp(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Protocol > BGP. TODO: implement."""
    pass


def tenant_policy_protocol_qos(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Protocol > Custom QoS. TODO: implement."""
    pass


def tenant_policy_protocol_dhcp(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Protocol > DHCP. TODO: implement."""
    pass


def tenant_policy_protocol_dataplane(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Protocol > Data Plane Policing. TODO: implement."""
    pass


def tenant_policy_protocol_eigrp(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Protocol > EIGRP. TODO: implement."""
    pass


def tenant_policy_protocol_endpoint_retention(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Protocol > End Point Retention. TODO: implement."""
    pass


def tenant_policy_protocol_firsthop_security(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Protocol > First Hop Security. TODO: implement."""
    pass


def tenant_policy_protocol_hsrp(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Protocol > HSRP. TODO: implement."""
    pass


def tenant_policy_protocol_igmp(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Protocol > IGMP. TODO: implement."""
    pass


def tenant_policy_protocol_ip_sla(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Protocol > IP SLA. TODO: implement."""
    pass


def tenant_policy_protocol_pbr(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Protocol > L4-L7 Policy-Based Redirect. TODO: implement."""
    pass


def tenant_policy_protocol_ospf(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Protocol > OSPF. TODO: implement."""
    pass


def tenant_policy_protocol_pim(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Protocol > PIM. TODO: implement."""
    pass


def tenant_policy_protocol_routemap_multicast(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Protocol > Route Maps for Multicast. TODO: implement."""
    pass


def tenant_policy_protocol_routemap_control(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Protocol > Route Maps for Route Control. TODO: implement."""
    pass


def tenant_policy_protocol_route_tag(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Protocol > Route Tag. TODO: implement."""
    pass


def tenant_policy_troubleshooting_span(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Troubleshooting SPAN. TODO: implement."""
    pass


def tenant_policy_troubleshooting_traceroute(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Troubleshooting Traceroute. TODO: implement."""
    pass


def tenant_policy_monitoring(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Monitoring. TODO: implement."""
    pass


def tenant_policy_netflow(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > NetFlow. TODO: implement."""
    pass


def tenant_policy_vmm(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > VMM. TODO: implement."""
    pass


def tenant_service_parameter(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Services > L4-L7 > Service Parameters. TODO: implement."""
    pass


def tenant_service_graph_template(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Services > L4-L7 > Service Graph Templates. TODO: implement."""
    pass


def tenant_service_router_configuration(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Services > L4-L7 > Router Configuration. TODO: implement."""
    pass


def tenant_service_function_profile(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Services > L4-L7 > Function Profiles. TODO: implement."""
    pass


def tenant_service_devices(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Services > L4-L7 > Devices. TODO: implement."""
    pass


def tenant_service_imported_device(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Services > L4-L7 > Imported Devices. TODO: implement."""
    pass


def tenant_service_device_policy(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Services > L4-L7 > Device Selection Policies. TODO: implement."""
    pass


def tenant_service_deployed_graph_instance(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Services > L4-L7 > Deployed Graph Instances. TODO: implement."""
    pass


def tenant_service_deployed_device(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Services > L4-L7 > Deployed Devices. TODO: implement."""
    pass


def tenant_service_device_manager(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Services > L4-L7 > Device Managers. TODO: implement."""
    pass


def tenant_service_chassis(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Policies > Services > L4-L7 > Chassis. TODO: implement."""
    pass


def tenant_node_management_epg(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Node Management EPGs. TODO: implement."""
    pass


def tenant_external_management_profile(builder: CobraBuilder, value: Any) -> None:
    """Tenants > External Management Network Instance Profiles. TODO: implement."""
    pass


def tenant_node_management_address(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Node Management Address. TODO: implement."""
    pass


def tenant_node_management_static(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Node Management Address > Static Node Management Address. TODO: implement."""
    pass


def tenant_node_connection_group(builder: CobraBuilder, value: Any) -> None:
    """Tenants > Managed Node Connectivity Groups. TODO: implement."""
    pass


# --------------------------------------------------------------------------- Fabric


def fabric_setup_pol(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Inventory > Pod Fabric Setup Policy."""
    Uni = cobra.model.pol.Uni(builder.root)
    Inst = cobra.model.ctrlr.Inst(Uni)
    for fabricSetupPol in value:
        SetupPol = cobra.model.fabric.SetupPol(Inst, **fabricSetupPol)
        builder.add(SetupPol)
        if "fabricSetupP" in fabricSetupPol:
            for fabricSetupP in fabricSetupPol["fabricSetupP"]:
                SetupP = cobra.model.fabric.SetupP(SetupPol, **fabricSetupP)
                builder.add(SetupP)


def fabric_rs_oos_path(builder: CobraBuilder, value: Any) -> None:
    """Fabric > RsOosPath."""
    Uni = cobra.model.pol.Uni(builder.root)
    Inst = cobra.model.fabric.Inst(Uni)
    OOServicePol = cobra.model.fabric.OOServicePol(Inst)
    for fabricRsOosPath in value:
        RsOosPath = cobra.model.fabric.RsOosPath(OOServicePol, **fabricRsOosPath)
        builder.add(RsOosPath)


def fabric_setup_p(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Inventory > Pod Fabric Setup Policy."""
    Uni = cobra.model.pol.Uni(builder.root)
    Inst = cobra.model.ctrlr.Inst(Uni)
    SetupPol = cobra.model.fabric.SetupPol(Inst)
    builder.add(SetupPol)
    for fabricSetupP in value:
        SetupP = cobra.model.fabric.SetupP(SetupPol, **fabricSetupP)
        builder.add(SetupP)


def fabric_node_ident_pol(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Inventory > Fabric Membership."""
    Uni = cobra.model.pol.Uni(builder.root)
    Inst = cobra.model.ctrlr.Inst(Uni)
    for fabricNodeIdentPol in value:
        NodeIdentPol = cobra.model.fabric.NodeIdentPol(Inst, **fabricNodeIdentPol)
        builder.add(NodeIdentPol)
        if "fabricNodeIdentP" in fabricNodeIdentPol:
            for fabricNodeIdentP in fabricNodeIdentPol["fabricNodeIdentP"]:
                NodeIdentP = cobra.model.fabric.NodeIdentP(NodeIdentPol, **fabricNodeIdentP)
                builder.add(NodeIdentP)


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
        builder.add(mo)


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
        builder.add(mo)


def fabric_switch_leaf_profile(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Fabric Policies > Switches > Leaf Switches > Profiles. TODO: implement."""
    pass


def fabric_switch_leaf_policy_group(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Fabric Policies > Switches > Leaf Switches > Policy Groups. TODO: implement."""
    pass


def fabric_switch_spine_profile(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Fabric Policies > Switches > Spine Switches > Profiles. TODO: implement."""
    pass


def fabric_switch_spine_policy_group(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Fabric Policies > Switches > Spine Switches > Policy Groups. TODO: implement."""
    pass


def fabric_module_leaf_profile(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Fabric Policies > Modules > Leaf Modules > Profiles. TODO: implement."""
    pass


def fabric_module_leaf_policy_group(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Fabric Policies > Modules > Leaf Modules > Policy Groups. TODO: implement."""
    pass


def fabric_module_spine_profile(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Fabric Policies > Modules > Spine Modules > Profiles. TODO: implement."""
    pass


def fabric_module_spine_policy_group(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Fabric Policies > Modules > Spine Modules > Policy Groups. TODO: implement."""
    pass


def fabric_interface_leaf_profile(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Fabric Policies > Interfaces > Leaf Interfaces > Profiles. TODO: implement."""
    pass


def fabric_interface_leaf_policy_group(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Fabric Policies > Interfaces > Leaf Interfaces > Policy Groups. TODO: implement."""
    pass


def fabric_interface_spine_profile(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Fabric Policies > Interfaces > Spine Interfaces > Profiles. TODO: implement."""
    pass


def fabric_interface_spine_policy_group(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Fabric Policies > Interfaces > Spine Interfaces > Policy Groups. TODO: implement."""
    pass


def datetime_pol(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Fabric Policies > Policies > Pod > Date and Time."""
    Inst = cobra.model.fabric.Inst(builder.uni)
    for datetimePol in value:
        Pol = cobra.model.datetime.Pol(Inst, **datetimePol)
        builder.add(Pol)
        if "datetimeNtpAuthKey" in datetimePol:
            for datetimeNtpAuthKey in datetimePol["datetimeNtpAuthKey"]:
                if not_nan_str(datetimeNtpAuthKey, ["id", "key", "trusted", "keyType"]):
                    NtpAuthKey = cobra.model.datetime.NtpAuthKey(Pol, **datetimeNtpAuthKey)
                    builder.add(NtpAuthKey)
        if "datetimeNtpProv" in datetimePol:
            for datetimeNtpProv in datetimePol["datetimeNtpProv"]:
                if not_nan_str(datetimeNtpProv, ["name"]):
                    NtpProv = cobra.model.datetime.NtpProv(Pol, **datetimeNtpProv)
                    builder.add(NtpProv)
                    if "datetimeRsNtpProvToNtpAuthKey" in datetimeNtpProv:
                        for key in datetimeNtpProv["datetimeRsNtpProvToNtpAuthKey"]:
                            if not_nan_str(key, ["tnDatetimeNtpAuthKeyId"]):
                                RsNtpProvToNtpAuthKey = cobra.model.datetime.RsNtpProvToNtpAuthKey(
                                    NtpProv, **key
                                )
                                builder.add(RsNtpProvToNtpAuthKey)
                    if "datetimeRsNtpProvToEpg" in datetimeNtpProv:
                        if not_nan_str(datetimeNtpProv["datetimeRsNtpProvToEpg"], ["tDn"]):
                            RsNtpProvToEpg = cobra.model.datetime.RsNtpProvToEpg(
                                NtpProv, **datetimeNtpProv["datetimeRsNtpProvToEpg"]
                            )
                            builder.add(RsNtpProvToEpg)


def snmp_pol(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Fabric Policies > Policies > Pod > SNMP."""
    Inst = cobra.model.fabric.Inst(builder.uni)
    for snmpPol in value:
        if not_nan_str(snmpPol, ["name"]):
            Pol = cobra.model.snmp.Pol(Inst, **snmpPol)
            builder.add(Pol)
            if "snmpClientGrpP" in snmpPol:
                for snmpClientGrpP in snmpPol["snmpClientGrpP"]:
                    if not_nan_str(snmpClientGrpP, ["name"]):
                        ClientGrpP = cobra.model.snmp.ClientGrpP(Pol, **snmpClientGrpP)
                        if "snmpRsEpg" in snmpClientGrpP:
                            if not_nan_str(snmpClientGrpP["snmpRsEpg"], ["tDn"]):
                                RsEpg = cobra.model.snmp.RsEpg(
                                    ClientGrpP, **snmpClientGrpP["snmpRsEpg"]
                                )
                                builder.add(RsEpg)
                        if "snmpClientP" in snmpClientGrpP:
                            for snmpClientP in snmpClientGrpP["snmpClientP"]:
                                if not_nan_str(snmpClientP, ["name", "addr"]):
                                    ClientP = cobra.model.snmp.ClientP(ClientGrpP, **snmpClientP)
                                    builder.add(ClientP)
            if "snmpUserP" in snmpPol:
                for snmpUserP in snmpPol["snmpUserP"]:
                    if not_nan_str(
                        snmpUserP, ["name", "privType", "privKey", "authType", "authKey"]
                    ):
                        UserP = cobra.model.snmp.UserP(Pol, **snmpUserP)
                        builder.add(UserP)
            if "snmpCommunityP" in snmpPol:
                for snmpCommunityP in snmpPol["snmpCommunityP"]:
                    if not_nan_str(snmpCommunityP, ["name"]):
                        CommunityP = cobra.model.snmp.CommunityP(Pol, **snmpCommunityP)
                        builder.add(CommunityP)
            if "snmpTrapFwdServerP" in snmpPol:
                for snmpTrapFwdServerP in snmpPol["snmpTrapFwdServerP"]:
                    if not_nan_str(snmpTrapFwdServerP, ["addr", "port"]):
                        TrapFwdServerP = cobra.model.snmp.TrapFwdServerP(Pol, **snmpTrapFwdServerP)
                        builder.add(TrapFwdServerP)


def comm_pol(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Fabric Policies > Policies > Pod > Management Access."""
    Inst = cobra.model.fabric.Inst(builder.uni)
    for commPol in value:
        Pol = cobra.model.comm.Pol(Inst, **commPol)
        builder.add(Pol)
        if "commTelnet" in commPol:
            if not_nan_str(commPol["commTelnet"], ["name", "adminSt"]):
                Telnet = cobra.model.comm.Telnet(Pol, **commPol["commTelnet"])
                builder.add(Telnet)
        if "commSsh" in commPol:
            if not_nan_str(commPol["commSsh"], ["name", "adminSt"]):
                Ssh = cobra.model.comm.Ssh(Pol, **commPol["commSsh"])
                builder.add(Ssh)
        if "commHttp" in commPol:
            if not_nan_str(commPol["commHttp"], ["name", "adminSt"]):
                Http = cobra.model.comm.Http(Pol, **commPol["commHttp"])
                builder.add(Http)
        if "commHttps" in commPol:
            if not_nan_str(commPol["commHttps"], ["name", "adminSt"]):
                Https = cobra.model.comm.Https(Pol, **commPol["commHttps"])
                builder.add(Https)
        if "commShellinabox" in commPol:
            if not_nan_str(commPol["commShellinabox"], ["name", "adminSt"]):
                Shellinabox = cobra.model.comm.Shellinabox(Pol, **commPol["commShellinabox"])
                builder.add(Shellinabox)


def fabric_policy_switch_callhome(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Fabric Policies > Policies > Switch > Callhome Inventory. TODO: implement."""
    pass


# --------------------------------------------------------------------------- Infra


def infra_node_p(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Switches > Leaf Switches > Profiles."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    for infraNodeP in value:
        NodeP = cobra.model.infra.NodeP(Infra, **infraNodeP)
        builder.add(NodeP)
        if "infraLeafS" in infraNodeP:
            for infraLeafS in infraNodeP["infraLeafS"]:
                if not_nan_str(infraLeafS, ["name"]):
                    LeafS = cobra.model.infra.LeafS(NodeP, **infraLeafS)
                    builder.add(LeafS)
                    if "infraNodeBlk" in infraLeafS:
                        if not_nan_str(infraLeafS["infraNodeBlk"], ["from_"]):
                            NodeBlk = cobra.model.infra.NodeBlk(LeafS, **infraLeafS["infraNodeBlk"])
                            builder.add(NodeBlk)
                    if "infraRsAccNodePGrp" in infraLeafS:
                        if not_nan_str(infraLeafS["infraRsAccNodePGrp"], ["tDn"]):
                            RsAccNodePGrp = cobra.model.infra.RsAccNodePGrp(
                                LeafS, **infraLeafS["infraRsAccNodePGrp"]
                            )
                            builder.add(RsAccNodePGrp)
        if "infraRsAccPortP" in infraNodeP:
            for infraRsAccPortP in infraNodeP["infraRsAccPortP"]:
                if not_nan_str(infraRsAccPortP, ["tDn"]):
                    RsAccPortP = cobra.model.infra.RsAccPortP(NodeP, **infraRsAccPortP)
                    builder.add(RsAccPortP)


def infra_acc_node_p_grp(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Switches > Leaf Switches > Policy Groups."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    FuncP = cobra.model.infra.FuncP(Infra)
    for infraAccNodePGrp in value:
        AccNodePGrp = cobra.model.infra.AccNodePGrp(FuncP, **infraAccNodePGrp)
        builder.add(AccNodePGrp)
        if "infraRsTopoctrlFwdScaleProfPol" in infraAccNodePGrp:
            if not_nan_str(
                infraAccNodePGrp["infraRsTopoctrlFwdScaleProfPol"],
                ["tnTopoctrlFwdScaleProfilePolName"],
            ):
                RsTopoctrlFwdScaleProfPol = cobra.model.infra.RsTopoctrlFwdScaleProfPol(
                    AccNodePGrp, **infraAccNodePGrp["infraRsTopoctrlFwdScaleProfPol"]
                )
                builder.add(RsTopoctrlFwdScaleProfPol)
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
                builder.add(RsLeafTopoctrlUsbConfigProfilePol)
        if "infraRsLeafPGrpToLldpIfPol" in infraAccNodePGrp:
            if not_nan_str(infraAccNodePGrp["infraRsLeafPGrpToLldpIfPol"], ["tnLldpIfPolName"]):
                RsLeafPGrpToLldpIfPol = cobra.model.infra.RsLeafPGrpToLldpIfPol(
                    AccNodePGrp, **infraAccNodePGrp["infraRsLeafPGrpToLldpIfPol"]
                )
                builder.add(RsLeafPGrpToLldpIfPol)
        if "infraRsBfdIpv6InstPol" in infraAccNodePGrp:
            if not_nan_str(infraAccNodePGrp["infraRsBfdIpv6InstPol"], ["tnBfdIpv6InstPolName"]):
                RsBfdIpv6InstPol = cobra.model.infra.RsBfdIpv6InstPol(
                    AccNodePGrp, **infraAccNodePGrp["infraRsBfdIpv6InstPol"]
                )
                builder.add(RsBfdIpv6InstPol)
        if "infraRsSynceInstPol" in infraAccNodePGrp:
            if not_nan_str(infraAccNodePGrp["infraRsSynceInstPol"], ["tnSynceInstPolName"]):
                RsSynceInstPol = cobra.model.infra.RsSynceInstPol(
                    AccNodePGrp, **infraAccNodePGrp["infraRsSynceInstPol"]
                )
                builder.add(RsSynceInstPol)
        if "infraRsPoeInstPol" in infraAccNodePGrp:
            if not_nan_str(infraAccNodePGrp["infraRsPoeInstPol"], ["tnPoeInstPolName"]):
                RsPoeInstPol = cobra.model.infra.RsPoeInstPol(
                    AccNodePGrp, **infraAccNodePGrp["infraRsPoeInstPol"]
                )
                builder.add(RsPoeInstPol)
        if "infraRsBfdMhIpv4InstPol" in infraAccNodePGrp:
            if not_nan_str(infraAccNodePGrp["infraRsBfdMhIpv4InstPol"], ["tnBfdMhIpv4InstPolName"]):
                RsBfdMhIpv4InstPol = cobra.model.infra.RsBfdMhIpv4InstPol(
                    AccNodePGrp, **infraAccNodePGrp["infraRsBfdMhIpv4InstPol"]
                )
                builder.add(RsBfdMhIpv4InstPol)
        if "infraRsBfdMhIpv6InstPol" in infraAccNodePGrp:
            if not_nan_str(infraAccNodePGrp["infraRsBfdMhIpv6InstPol"], ["tnBfdMhIpv6InstPolName"]):
                RsBfdMhIpv6InstPol = cobra.model.infra.RsBfdMhIpv6InstPol(
                    AccNodePGrp, **infraAccNodePGrp["infraRsBfdMhIpv6InstPol"]
                )
                builder.add(RsBfdMhIpv6InstPol)
        if "infraRsEquipmentFlashConfigPol" in infraAccNodePGrp:
            if not_nan_str(
                infraAccNodePGrp["infraRsEquipmentFlashConfigPol"],
                ["tnEquipmentFlashConfigPolName"],
            ):
                RsEquipmentFlashConfigPol = cobra.model.infra.RsEquipmentFlashConfigPol(
                    AccNodePGrp, **infraAccNodePGrp["infraRsEquipmentFlashConfigPol"]
                )
                builder.add(RsEquipmentFlashConfigPol)
        if "infraRsMonNodeInfraPol" in infraAccNodePGrp:
            if not_nan_str(infraAccNodePGrp["infraRsMonNodeInfraPol"], ["tnMonInfraPolName"]):
                RsMonNodeInfraPol = cobra.model.infra.RsMonNodeInfraPol(
                    AccNodePGrp, **infraAccNodePGrp["infraRsMonNodeInfraPol"]
                )
                builder.add(RsMonNodeInfraPol)
        if "infraRsFcInstPol" in infraAccNodePGrp:
            if not_nan_str(infraAccNodePGrp["infraRsFcInstPol"], ["tnFcInstPolName"]):
                RsFcInstPol = cobra.model.infra.RsFcInstPol(
                    AccNodePGrp, **infraAccNodePGrp["infraRsFcInstPol"]
                )
                builder.add(RsFcInstPol)
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
                builder.add(RsTopoctrlFastLinkFailoverInstPol)
        if "infraRsMstInstPol" in infraAccNodePGrp:
            if not_nan_str(infraAccNodePGrp["infraRsMstInstPol"], ["tnStpInstPolName"]):
                RsMstInstPol = cobra.model.infra.RsMstInstPol(
                    AccNodePGrp, **infraAccNodePGrp["infraRsMstInstPol"]
                )
                builder.add(RsMstInstPol)
        if "infraRsFcFabricPol" in infraAccNodePGrp:
            if not_nan_str(infraAccNodePGrp["infraRsFcFabricPol"], ["tnFcFabricPolName"]):
                RsFcFabricPol = cobra.model.infra.RsFcFabricPol(
                    AccNodePGrp, **infraAccNodePGrp["infraRsFcFabricPol"]
                )
                builder.add(RsFcFabricPol)
        if "infraRsLeafCoppProfile" in infraAccNodePGrp:
            if not_nan_str(infraAccNodePGrp["infraRsLeafCoppProfile"], ["tnCoppLeafProfileName"]):
                RsLeafCoppProfile = cobra.model.infra.RsLeafCoppProfile(
                    AccNodePGrp, **infraAccNodePGrp["infraRsLeafCoppProfile"]
                )
                builder.add(RsLeafCoppProfile)
        if "infraRsIaclLeafProfile" in infraAccNodePGrp:
            if not_nan_str(infraAccNodePGrp["infraRsIaclLeafProfile"], ["tnIaclLeafProfileName"]):
                RsIaclLeafProfile = cobra.model.infra.RsIaclLeafProfile(
                    AccNodePGrp, **infraAccNodePGrp["infraRsIaclLeafProfile"]
                )
                builder.add(RsIaclLeafProfile)
        if "infraRsBfdIpv4InstPol" in infraAccNodePGrp:
            if not_nan_str(infraAccNodePGrp["infraRsBfdIpv4InstPol"], ["tnBfdIpv4InstPolName"]):
                RsBfdIpv4InstPol = cobra.model.infra.RsBfdIpv4InstPol(
                    AccNodePGrp, **infraAccNodePGrp["infraRsBfdIpv4InstPol"]
                )
                builder.add(RsBfdIpv4InstPol)
        if "infraRsL2NodeAuthPol" in infraAccNodePGrp:
            if not_nan_str(infraAccNodePGrp["infraRsL2NodeAuthPol"], ["tnL2NodeAuthPolName"]):
                RsL2NodeAuthPol = cobra.model.infra.RsL2NodeAuthPol(
                    AccNodePGrp, **infraAccNodePGrp["infraRsL2NodeAuthPol"]
                )
                builder.add(RsL2NodeAuthPol)
        if "infraRsLeafPGrpToCdpIfPol" in infraAccNodePGrp:
            if not_nan_str(infraAccNodePGrp["infraRsLeafPGrpToCdpIfPol"], ["tnCdpIfPolName"]):
                RsLeafPGrpToCdpIfPol = cobra.model.infra.RsLeafPGrpToCdpIfPol(
                    AccNodePGrp, **infraAccNodePGrp["infraRsLeafPGrpToCdpIfPol"]
                )
                builder.add(RsLeafPGrpToCdpIfPol)


def infra_spine_p(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Switches > Spine Switches > Profiles."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    for infraSpineP in value:
        SpineP = cobra.model.infra.SpineP(Infra, **infraSpineP)
        builder.add(SpineP)
        if "infraSpineS" in infraSpineP:
            for infraSpineS in infraSpineP["infraSpineS"]:
                SpineS = cobra.model.infra.SpineS(SpineP, **infraSpineS)
                builder.add(SpineS)
                if "infraRsSpineAccNodePGrp" in infraSpineS:
                    RsSpineAccNodePGrp = cobra.model.infra.RsSpineAccNodePGrp(
                        SpineS, **infraSpineS["infraRsSpineAccNodePGrp"]
                    )
                    builder.add(RsSpineAccNodePGrp)
                if "infraNodeBlk" in infraSpineS:
                    NodeBlk = cobra.model.infra.NodeBlk(SpineS, **infraSpineS["infraNodeBlk"])
                    builder.add(NodeBlk)
        if "infraRsSpAccPortP" in infraSpineP:
            RsSpAccPortP = cobra.model.infra.RsSpAccPortP(
                SpineP, **infraSpineP["infraRsSpAccPortP"]
            )
            builder.add(RsSpAccPortP)


def infra_spine_acc_node_p_grp(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Switches > Spine Switches > Policy Groups."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    FuncP = cobra.model.infra.FuncP(Infra)
    for infraSpineAccNodePGrp in value:
        SpineAccNodePGrp = cobra.model.infra.SpineAccNodePGrp(FuncP, **infraSpineAccNodePGrp)
        builder.add(SpineAccNodePGrp)
        if "infraRsSpineCoppProfile" in infraSpineAccNodePGrp:
            RsSpineCoppProfile = cobra.model.infra.RsSpineCoppProfile(
                SpineAccNodePGrp, **infraSpineAccNodePGrp["infraRsSpineCoppProfile"]
            )
            builder.add(RsSpineCoppProfile)
        if "infraRsSpineBfdIpv4InstPol" in infraSpineAccNodePGrp:
            RsSpineBfdIpv4InstPol = cobra.model.infra.RsSpineBfdIpv4InstPol(
                SpineAccNodePGrp, **infraSpineAccNodePGrp["infraRsSpineBfdIpv4InstPol"]
            )
            builder.add(RsSpineBfdIpv4InstPol)
        if "infraRsSpineBfdIpv6InstPol" in infraSpineAccNodePGrp:
            RsSpineBfdIpv6InstPol = cobra.model.infra.RsSpineBfdIpv6InstPol(
                SpineAccNodePGrp, **infraSpineAccNodePGrp["infraRsSpineBfdIpv6InstPol"]
            )
            builder.add(RsSpineBfdIpv6InstPol)
        if "infraRsIaclSpineProfile" in infraSpineAccNodePGrp:
            RsIaclSpineProfile = cobra.model.infra.RsIaclSpineProfile(
                SpineAccNodePGrp, **infraSpineAccNodePGrp["infraRsIaclSpineProfile"]
            )
            builder.add(RsIaclSpineProfile)
        if "infraRsSpinePGrpToCdpIfPol" in infraSpineAccNodePGrp:
            RsSpinePGrpToCdpIfPol = cobra.model.infra.RsSpinePGrpToCdpIfPol(
                SpineAccNodePGrp, **infraSpineAccNodePGrp["infraRsSpinePGrpToCdpIfPol"]
            )
            builder.add(RsSpinePGrpToCdpIfPol)
        if "infraRsSpinePGrpToLldpIfPol" in infraSpineAccNodePGrp:
            RsSpinePGrpToLldpIfPol = cobra.model.infra.RsSpinePGrpToLldpIfPol(
                SpineAccNodePGrp, **infraSpineAccNodePGrp["infraRsSpinePGrpToLldpIfPol"]
            )
            builder.add(RsSpinePGrpToLldpIfPol)


def infra_sp_acc_port_p(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Interfaces > Spine Interfaces > Profiles."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    for infraSpAccPortP in value:
        SpAccPortP = cobra.model.infra.SpAccPortP(Infra, **infraSpAccPortP)
        builder.add(SpAccPortP)
        if "infraSHPortS" in infraSpAccPortP:
            for infraSHPortS in infraSpAccPortP["infraSHPortS"]:
                SHPortS = cobra.model.infra.SHPortS(SpAccPortP, **infraSHPortS)
                builder.add(SHPortS)
                if "infraRsSpAccGrp" in infraSHPortS:
                    RsSpAccGrp = cobra.model.infra.RsSpAccGrp(
                        SHPortS, **infraSHPortS["infraRsSpAccGrp"]
                    )
                    builder.add(RsSpAccGrp)
                if "infraPortBlk" in infraSHPortS:
                    for infraPortBlk in infraSHPortS["infraPortBlk"]:
                        PortBlk = cobra.model.infra.PortBlk(SHPortS, **infraPortBlk)
                        builder.add(PortBlk)


def infra_sp_acc_port_grp(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Interfaces > Spine Interfaces > Policy Groups."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    FuncP = cobra.model.infra.FuncP(Infra)
    for infraSpAccPortGrp in value:
        SpAccPortGrp = cobra.model.infra.SpAccPortGrp(FuncP, **infraSpAccPortGrp)
        builder.add(SpAccPortGrp)
        if "infraRsHIfPol" in infraSpAccPortGrp:
            RsHIfPol = cobra.model.infra.RsHIfPol(
                SpAccPortGrp, **infraSpAccPortGrp["infraRsHIfPol"]
            )
            builder.add(RsHIfPol)
        if "infraRsCdpIfPol" in infraSpAccPortGrp:
            RsCdpIfPol = cobra.model.infra.RsCdpIfPol(
                SpAccPortGrp, **infraSpAccPortGrp["infraRsCdpIfPol"]
            )
            builder.add(RsCdpIfPol)
        if "infraRsMacsecIfPol" in infraSpAccPortGrp:
            RsMacsecIfPol = cobra.model.infra.RsMacsecIfPol(
                SpAccPortGrp, **infraSpAccPortGrp["infraRsMacsecIfPol"]
            )
            builder.add(RsMacsecIfPol)
        if "infraRsAttEntP" in infraSpAccPortGrp:
            RsAttEntP = cobra.model.infra.RsAttEntP(
                SpAccPortGrp, **infraSpAccPortGrp["infraRsAttEntP"]
            )
            builder.add(RsAttEntP)
        if "infraRsLinkFlapPol" in infraSpAccPortGrp:
            RsLinkFlapPol = cobra.model.infra.RsLinkFlapPol(
                SpAccPortGrp, **infraSpAccPortGrp["infraRsLinkFlapPol"]
            )
            builder.add(RsLinkFlapPol)
        if "infraRsCoppIfPol" in infraSpAccPortGrp:
            RsCoppIfPol = cobra.model.infra.RsCoppIfPol(
                SpAccPortGrp, **infraSpAccPortGrp["infraRsCoppIfPol"]
            )
            builder.add(RsCoppIfPol)


def infra_acc_port_p(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Interfaces > Leaf Interfaces > Profiles."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    for infraAccPortP in value:
        AccPortP = cobra.model.infra.AccPortP(Infra, **infraAccPortP)
        builder.add(AccPortP)
        if "infraHPortS" in infraAccPortP:
            for infraHPortS in infraAccPortP["infraHPortS"]:
                HPortS = cobra.model.infra.HPortS(AccPortP, **infraHPortS)
                builder.add(HPortS)
                if "infraRsAccBaseGrp" in infraHPortS:
                    if not_nan_str(infraHPortS["infraRsAccBaseGrp"], ["tDn"]):
                        RsAccBaseGrp = cobra.model.infra.RsAccBaseGrp(
                            HPortS, **infraHPortS["infraRsAccBaseGrp"]
                        )
                        builder.add(RsAccBaseGrp)
                if "infraPortBlk" in infraHPortS:
                    for infraPortBlk in infraHPortS["infraPortBlk"]:
                        if not_nan_str(infraPortBlk, ["fromPort"]):
                            PortBlk = cobra.model.infra.PortBlk(HPortS, **infraPortBlk)
                            builder.add(PortBlk)


def infra_fex_p(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Interfaces > Leaf Interfaces > FEX Profiles."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    for infraFexP in value:
        FexP = cobra.model.infra.FexP(Infra, **infraFexP)
        builder.add(FexP)
        if "infraHPortS" in infraFexP:
            for infraHPortS in infraFexP["infraHPortS"]:
                HPortS = cobra.model.infra.HPortS(FexP, **infraHPortS)
                builder.add(HPortS)
                if "infraRsAccBaseGrp" in infraHPortS:
                    RsAccBaseGrp = cobra.model.infra.RsAccBaseGrp(
                        HPortS, **infraHPortS["infraRsAccBaseGrp"]
                    )
                    builder.add(RsAccBaseGrp)
                if "infraPortBlk" in infraHPortS:
                    for block in infraHPortS["infraPortBlk"]:
                        PortBlk = cobra.model.infra.PortBlk(HPortS, **block)
                        builder.add(PortBlk)
        if "infraFexBndlGrp" in infraFexP:
            FexBndlGrp = cobra.model.infra.FexBndlGrp(FexP, **infraFexP["infraFexBndlGrp"])
            builder.add(FexBndlGrp)


def infra_acc_port_grp(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Interfaces > Leaf Interfaces > Policy Groups > Access."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    FuncP = cobra.model.infra.FuncP(Infra)
    for infraAccPortGrp in value:
        AccPortGrp = cobra.model.infra.AccPortGrp(FuncP, **infraAccPortGrp)
        builder.add(AccPortGrp)
        if "infraRsAttEntP" in infraAccPortGrp:
            if not_nan_str(infraAccPortGrp["infraRsAttEntP"], ["tDn"]):
                RsAttEntP = cobra.model.infra.RsAttEntP(
                    AccPortGrp, **infraAccPortGrp["infraRsAttEntP"]
                )
                builder.add(RsAttEntP)
        if "infraRsStpIfPol" in infraAccPortGrp:
            if not_nan_str(infraAccPortGrp["infraRsStpIfPol"], ["tnStpIfPolName"]):
                RsStpIfPol = cobra.model.infra.RsStpIfPol(
                    AccPortGrp, **infraAccPortGrp["infraRsStpIfPol"]
                )
                builder.add(RsStpIfPol)
        if "infraRsQosLlfcIfPol" in infraAccPortGrp:
            if not_nan_str(infraAccPortGrp["infraRsQosLlfcIfPol"], ["tnQosLlfcIfPolName"]):
                RsQosLlfcIfPol = cobra.model.infra.RsQosLlfcIfPol(
                    AccPortGrp, **infraAccPortGrp["infraRsQosLlfcIfPol"]
                )
                builder.add(RsQosLlfcIfPol)
        if "infraRsQosIngressDppIfPol" in infraAccPortGrp:
            if not_nan_str(infraAccPortGrp["infraRsQosIngressDppIfPol"], ["tnQosDppPolName"]):
                RsQosIngressDppIfPol = cobra.model.infra.RsQosIngressDppIfPol(
                    AccPortGrp, **infraAccPortGrp["infraRsQosIngressDppIfPol"]
                )
                builder.add(RsQosIngressDppIfPol)
        if "infraRsStormctrlIfPol" in infraAccPortGrp:
            if not_nan_str(infraAccPortGrp["infraRsStormctrlIfPol"], ["tnStormctrlIfPolName"]):
                RsStormctrlIfPol = cobra.model.infra.RsStormctrlIfPol(
                    AccPortGrp, **infraAccPortGrp["infraRsStormctrlIfPol"]
                )
                builder.add(RsStormctrlIfPol)
        if "infraRsQosEgressDppIfPol" in infraAccPortGrp:
            if not_nan_str(infraAccPortGrp["infraRsQosEgressDppIfPol"], ["tnQosDppPolName"]):
                RsQosEgressDppIfPol = cobra.model.infra.RsQosEgressDppIfPol(
                    AccPortGrp, **infraAccPortGrp["infraRsQosEgressDppIfPol"]
                )
                builder.add(RsQosEgressDppIfPol)
        if "infraRsMonIfInfraPol" in infraAccPortGrp:
            if not_nan_str(infraAccPortGrp["infraRsMonIfInfraPol"], ["tnMonInfraPolName"]):
                RsMonIfInfraPol = cobra.model.infra.RsMonIfInfraPol(
                    AccPortGrp, **infraAccPortGrp["infraRsMonIfInfraPol"]
                )
                builder.add(RsMonIfInfraPol)
        if "infraRsMcpIfPol" in infraAccPortGrp:
            if not_nan_str(infraAccPortGrp["infraRsMcpIfPol"], ["tnMcpIfPolName"]):
                RsMcpIfPol = cobra.model.infra.RsMcpIfPol(
                    AccPortGrp, **infraAccPortGrp["infraRsMcpIfPol"]
                )
                builder.add(RsMcpIfPol)
        if "infraRsMacsecIfPol" in infraAccPortGrp:
            if not_nan_str(infraAccPortGrp["infraRsMacsecIfPol"], ["tnMacsecIfPolName"]):
                RsMacsecIfPol = cobra.model.infra.RsMacsecIfPol(
                    AccPortGrp, **infraAccPortGrp["infraRsMacsecIfPol"]
                )
                builder.add(RsMacsecIfPol)
        if "infraRsQosSdIfPol" in infraAccPortGrp:
            if not_nan_str(infraAccPortGrp["infraRsQosSdIfPol"], ["tnQosSdIfPolName"]):
                RsQosSdIfPol = cobra.model.infra.RsQosSdIfPol(
                    AccPortGrp, **infraAccPortGrp["infraRsQosSdIfPol"]
                )
                builder.add(RsQosSdIfPol)
        if "infraRsCdpIfPol" in infraAccPortGrp:
            if not_nan_str(infraAccPortGrp["infraRsCdpIfPol"], ["tnCdpIfPolName"]):
                RsCdpIfPol = cobra.model.infra.RsCdpIfPol(
                    AccPortGrp, **infraAccPortGrp["infraRsCdpIfPol"]
                )
                builder.add(RsCdpIfPol)
        if "infraRsL2IfPol" in infraAccPortGrp:
            if not_nan_str(infraAccPortGrp["infraRsL2IfPol"], ["tnL2IfPolName"]):
                RsL2IfPol = cobra.model.infra.RsL2IfPol(
                    AccPortGrp, **infraAccPortGrp["infraRsL2IfPol"]
                )
                builder.add(RsL2IfPol)
        if "infraRsQosDppIfPol" in infraAccPortGrp:
            if not_nan_str(infraAccPortGrp["infraRsQosDppIfPol"], ["tnQosDppPolName"]):
                RsQosDppIfPol = cobra.model.infra.RsQosDppIfPol(
                    AccPortGrp, **infraAccPortGrp["infraRsQosDppIfPol"]
                )
                builder.add(RsQosDppIfPol)
        if "infraRsCoppIfPol" in infraAccPortGrp:
            if not_nan_str(infraAccPortGrp["infraRsCoppIfPol"], ["tnCoppIfPolName"]):
                RsCoppIfPol = cobra.model.infra.RsCoppIfPol(
                    AccPortGrp, **infraAccPortGrp["infraRsCoppIfPol"]
                )
                builder.add(RsCoppIfPol)
        if "infraRsDwdmIfPol" in infraAccPortGrp:
            if not_nan_str(infraAccPortGrp["infraRsDwdmIfPol"], ["tnDwdmIfPolName"]):
                RsDwdmIfPol = cobra.model.infra.RsDwdmIfPol(
                    AccPortGrp, **infraAccPortGrp["infraRsDwdmIfPol"]
                )
                builder.add(RsDwdmIfPol)
        if "infraRsLinkFlapPol" in infraAccPortGrp:
            if not_nan_str(infraAccPortGrp["infraRsLinkFlapPol"], ["tnFabricLinkFlapPolName"]):
                RsLinkFlapPol = cobra.model.infra.RsLinkFlapPol(
                    AccPortGrp, **infraAccPortGrp["infraRsLinkFlapPol"]
                )
                builder.add(RsLinkFlapPol)
        if "infraRsLldpIfPol" in infraAccPortGrp:
            if not_nan_str(infraAccPortGrp["infraRsLldpIfPol"], ["tnLldpIfPolName"]):
                RsLldpIfPol = cobra.model.infra.RsLldpIfPol(
                    AccPortGrp, **infraAccPortGrp["infraRsLldpIfPol"]
                )
                builder.add(RsLldpIfPol)
        if "infraRsFcIfPol" in infraAccPortGrp:
            if not_nan_str(infraAccPortGrp["infraRsFcIfPol"], ["tnFcIfPolName"]):
                RsFcIfPol = cobra.model.infra.RsFcIfPol(
                    AccPortGrp, **infraAccPortGrp["infraRsFcIfPol"]
                )
                builder.add(RsFcIfPol)
        if "infraRsQosPfcIfPol" in infraAccPortGrp:
            if not_nan_str(infraAccPortGrp["infraRsQosPfcIfPol"], ["tnQosPfcIfPolName"]):
                RsQosPfcIfPol = cobra.model.infra.RsQosPfcIfPol(
                    AccPortGrp, **infraAccPortGrp["infraRsQosPfcIfPol"]
                )
                builder.add(RsQosPfcIfPol)
        if "infraRsHIfPol" in infraAccPortGrp:
            if not_nan_str(infraAccPortGrp["infraRsHIfPol"], ["tnFabricHIfPolName"]):
                RsHIfPol = cobra.model.infra.RsHIfPol(
                    AccPortGrp, **infraAccPortGrp["infraRsHIfPol"]
                )
                builder.add(RsHIfPol)
        if "infraRsL2PortSecurityPol" in infraAccPortGrp:
            if not_nan_str(
                infraAccPortGrp["infraRsL2PortSecurityPol"], ["tnL2PortSecurityPolName"]
            ):
                RsL2PortSecurityPol = cobra.model.infra.RsL2PortSecurityPol(
                    AccPortGrp, **infraAccPortGrp["infraRsL2PortSecurityPol"]
                )
                builder.add(RsL2PortSecurityPol)
        if "infraRsL2PortAuthPol" in infraAccPortGrp:
            if not_nan_str(infraAccPortGrp["infraRsL2PortAuthPol"], ["tnL2PortAuthPolName"]):
                RsL2PortAuthPol = cobra.model.infra.RsL2PortAuthPol(
                    AccPortGrp, **infraAccPortGrp["infraRsL2PortAuthPol"]
                )
                builder.add(RsL2PortAuthPol)


def infra_acc_bndl_grp(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Interfaces > Leaf Interfaces > Policy Groups > PC or VPC."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    FuncP = cobra.model.infra.FuncP(Infra)
    for infraAccBndlGrp in value:
        AccBndlGrp = cobra.model.infra.AccBndlGrp(FuncP, **infraAccBndlGrp)
        builder.add(AccBndlGrp)
        if "infraRsAttEntP" in infraAccBndlGrp:
            if not_nan_str(infraAccBndlGrp["infraRsAttEntP"], ["tDn"]):
                RsAttEntP = cobra.model.infra.RsAttEntP(
                    AccBndlGrp, **infraAccBndlGrp["infraRsAttEntP"]
                )
                builder.add(RsAttEntP)
        if "infraRsStpIfPol" in infraAccBndlGrp:
            if not_nan_str(infraAccBndlGrp["infraRsStpIfPol"], ["tnStpIfPolName"]):
                RsStpIfPol = cobra.model.infra.RsStpIfPol(
                    AccBndlGrp, **infraAccBndlGrp["infraRsStpIfPol"]
                )
                builder.add(RsStpIfPol)
        if "infraRsQosLlfcIfPol" in infraAccBndlGrp:
            if not_nan_str(infraAccBndlGrp["infraRsQosLlfcIfPol"], ["tnQosLlfcIfPolName"]):
                RsQosLlfcIfPol = cobra.model.infra.RsQosLlfcIfPol(
                    AccBndlGrp, **infraAccBndlGrp["infraRsQosLlfcIfPol"]
                )
                builder.add(RsQosLlfcIfPol)
        if "infraRsQosIngressDppIfPol" in infraAccBndlGrp:
            if not_nan_str(infraAccBndlGrp["infraRsQosIngressDppIfPol"], ["tnQosDppPolName"]):
                RsQosIngressDppIfPol = cobra.model.infra.RsQosIngressDppIfPol(
                    AccBndlGrp, **infraAccBndlGrp["infraRsQosIngressDppIfPol"]
                )
                builder.add(RsQosIngressDppIfPol)
        if "infraRsStormctrlIfPol" in infraAccBndlGrp:
            if not_nan_str(infraAccBndlGrp["infraRsStormctrlIfPol"], ["tnStormctrlIfPolName"]):
                RsStormctrlIfPol = cobra.model.infra.RsStormctrlIfPol(
                    AccBndlGrp, **infraAccBndlGrp["infraRsStormctrlIfPol"]
                )
                builder.add(RsStormctrlIfPol)
        if "infraRsQosEgressDppIfPol" in infraAccBndlGrp:
            if not_nan_str(infraAccBndlGrp["infraRsQosEgressDppIfPol"], ["tnQosDppPolName"]):
                RsQosEgressDppIfPol = cobra.model.infra.RsQosEgressDppIfPol(
                    AccBndlGrp, **infraAccBndlGrp["infraRsQosEgressDppIfPol"]
                )
                builder.add(RsQosEgressDppIfPol)
        if "infraRsMonIfInfraPol" in infraAccBndlGrp:
            if not_nan_str(infraAccBndlGrp["infraRsMonIfInfraPol"], ["tnMonInfraPolName"]):
                RsMonIfInfraPol = cobra.model.infra.RsMonIfInfraPol(
                    AccBndlGrp, **infraAccBndlGrp["infraRsMonIfInfraPol"]
                )
                builder.add(RsMonIfInfraPol)
        if "infraRsMcpIfPol" in infraAccBndlGrp:
            if not_nan_str(infraAccBndlGrp["infraRsMcpIfPol"], ["tnMcpIfPolName"]):
                RsMcpIfPol = cobra.model.infra.RsMcpIfPol(
                    AccBndlGrp, **infraAccBndlGrp["infraRsMcpIfPol"]
                )
                builder.add(RsMcpIfPol)
        if "infraRsMacsecIfPol" in infraAccBndlGrp:
            if not_nan_str(infraAccBndlGrp["infraRsMacsecIfPol"], ["tnMacsecIfPolName"]):
                RsMacsecIfPol = cobra.model.infra.RsMacsecIfPol(
                    AccBndlGrp, **infraAccBndlGrp["infraRsMacsecIfPol"]
                )
                builder.add(RsMacsecIfPol)
        if "infraRsQosSdIfPol" in infraAccBndlGrp:
            if not_nan_str(infraAccBndlGrp["infraRsQosSdIfPol"], ["tnQosSdIfPolName"]):
                RsQosSdIfPol = cobra.model.infra.RsQosSdIfPol(
                    AccBndlGrp, **infraAccBndlGrp["infraRsQosSdIfPol"]
                )
                builder.add(RsQosSdIfPol)
        if "infraRsCdpIfPol" in infraAccBndlGrp:
            if not_nan_str(infraAccBndlGrp["infraRsCdpIfPol"], ["tnCdpIfPolName"]):
                RsCdpIfPol = cobra.model.infra.RsCdpIfPol(
                    AccBndlGrp, **infraAccBndlGrp["infraRsCdpIfPol"]
                )
                builder.add(RsCdpIfPol)
        if "infraRsL2IfPol" in infraAccBndlGrp:
            if not_nan_str(infraAccBndlGrp["infraRsL2IfPol"], ["tnL2IfPolName"]):
                RsL2IfPol = cobra.model.infra.RsL2IfPol(
                    AccBndlGrp, **infraAccBndlGrp["infraRsL2IfPol"]
                )
                builder.add(RsL2IfPol)
        if "infraRsQosDppIfPol" in infraAccBndlGrp:
            if not_nan_str(infraAccBndlGrp["infraRsQosDppIfPol"], ["tnQosDppPolName"]):
                RsQosDppIfPol = cobra.model.infra.RsQosDppIfPol(
                    AccBndlGrp, **infraAccBndlGrp["infraRsQosDppIfPol"]
                )
                builder.add(RsQosDppIfPol)
        if "infraRsCoppIfPol" in infraAccBndlGrp:
            if not_nan_str(infraAccBndlGrp["infraRsCoppIfPol"], ["tnCoppIfPolName"]):
                RsCoppIfPol = cobra.model.infra.RsCoppIfPol(
                    AccBndlGrp, **infraAccBndlGrp["infraRsCoppIfPol"]
                )
                builder.add(RsCoppIfPol)
        if "infraRsLldpIfPol" in infraAccBndlGrp:
            if not_nan_str(infraAccBndlGrp["infraRsLldpIfPol"], ["tnLldpIfPolName"]):
                RsLldpIfPol = cobra.model.infra.RsLldpIfPol(
                    AccBndlGrp, **infraAccBndlGrp["infraRsLldpIfPol"]
                )
                builder.add(RsLldpIfPol)
        if "infraRsFcIfPol" in infraAccBndlGrp:
            if not_nan_str(infraAccBndlGrp["infraRsFcIfPol"], ["tnFcIfPolName"]):
                RsFcIfPol = cobra.model.infra.RsFcIfPol(
                    AccBndlGrp, **infraAccBndlGrp["infraRsFcIfPol"]
                )
                builder.add(RsFcIfPol)
        if "infraRsQosPfcIfPol" in infraAccBndlGrp:
            if not_nan_str(infraAccBndlGrp["infraRsQosPfcIfPol"], ["tnQosPfcIfPolName"]):
                RsQosPfcIfPol = cobra.model.infra.RsQosPfcIfPol(
                    AccBndlGrp, **infraAccBndlGrp["infraRsQosPfcIfPol"]
                )
                builder.add(RsQosPfcIfPol)
        if "infraRsHIfPol" in infraAccBndlGrp:
            if not_nan_str(infraAccBndlGrp["infraRsHIfPol"], ["tnFabricHIfPolName"]):
                RsHIfPol = cobra.model.infra.RsHIfPol(
                    AccBndlGrp, **infraAccBndlGrp["infraRsHIfPol"]
                )
                builder.add(RsHIfPol)
        if "infraRsL2PortSecurityPol" in infraAccBndlGrp:
            if not_nan_str(
                infraAccBndlGrp["infraRsL2PortSecurityPol"], ["tnL2PortSecurityPolName"]
            ):
                RsL2PortSecurityPol = cobra.model.infra.RsL2PortSecurityPol(
                    AccBndlGrp, **infraAccBndlGrp["infraRsL2PortSecurityPol"]
                )
                builder.add(RsL2PortSecurityPol)
        if "infraRsL2PortAuthPol" in infraAccBndlGrp:
            if not_nan_str(infraAccBndlGrp["infraRsL2PortAuthPol"], ["tnL2PortAuthPolName"]):
                RsL2PortAuthPol = cobra.model.infra.RsL2PortAuthPol(
                    AccBndlGrp, **infraAccBndlGrp["infraRsL2PortAuthPol"]
                )
                builder.add(RsL2PortAuthPol)
        if "infraRsLacpPol" in infraAccBndlGrp:
            if not_nan_str(infraAccBndlGrp["infraRsLacpPol"], ["tnLacpLagPolName"]):
                RsLacpPol = cobra.model.infra.RsLacpPol(
                    AccBndlGrp, **infraAccBndlGrp["infraRsLacpPol"]
                )
                builder.add(RsLacpPol)
        if "infraRsLinkFlapPol" in infraAccBndlGrp:
            if not_nan_str(infraAccBndlGrp["infraRsLinkFlapPol"], ["tnFabricLinkFlapPolName"]):
                RsLinkFlapPol = cobra.model.infra.RsLinkFlapPol(
                    AccBndlGrp, **infraAccBndlGrp["infraRsLinkFlapPol"]
                )
                builder.add(RsLinkFlapPol)


def infra_att_entity_p(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Policies > Global > Attachable Access Entity Profiles."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    for infraAttEntityP in value:
        AttEntityP = cobra.model.infra.AttEntityP(Infra, **infraAttEntityP)
        builder.add(AttEntityP)
        if "infraRsDomP" in infraAttEntityP:
            for infraRsDomP in infraAttEntityP["infraRsDomP"]:
                RsDomP = cobra.model.infra.RsDomP(AttEntityP, **infraRsDomP)
                builder.add(RsDomP)


def fvns_vlan_inst_p(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Pools > VLAN."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    for fvnsVlanInstP in value:
        VlanInstP = cobra.model.fvns.VlanInstP(Infra, **fvnsVlanInstP)
        builder.add(VlanInstP)
        if "fvnsEncapBlk" in fvnsVlanInstP:
            for fvnsEncapBlk in fvnsVlanInstP["fvnsEncapBlk"]:
                EncapBlk = cobra.model.fvns.EncapBlk(VlanInstP, **fvnsEncapBlk)
                builder.add(EncapBlk)


def phys_dom_p(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Physical and External Domains > Physical Domain."""
    Uni = cobra.model.pol.Uni(builder.root)
    for physDomP in value:
        DomP = cobra.model.phys.DomP(Uni, **physDomP)
        builder.add(DomP)
        if "infraRsVlanNs" in physDomP:
            RsVlanNs = cobra.model.infra.RsVlanNs(DomP, **physDomP["infraRsVlanNs"])
            builder.add(RsVlanNs)


def l3ext_dom_p(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Physical and External Domains > L3 Domains."""
    Uni = cobra.model.pol.Uni(builder.root)
    for l3extDomP in value:
        DomP = cobra.model.l3ext.DomP(Uni, **l3extDomP)
        builder.add(DomP)
        if "infraRsVlanNs" in l3extDomP:
            RsVlanNs = cobra.model.infra.RsVlanNs(DomP, **l3extDomP["infraRsVlanNs"])
            builder.add(RsVlanNs)


def l2ext_dom_p(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Physical and External Domains > External Bridged Domains."""
    Uni = cobra.model.pol.Uni(builder.root)
    for l2extDomP in value:
        DomP = cobra.model.l2ext.DomP(Uni, **l2extDomP)
        builder.add(DomP)
        if "infraRsVlanNs" in l2extDomP:
            RsVlanNs = cobra.model.infra.RsVlanNs(DomP, **l2extDomP["infraRsVlanNs"])
            builder.add(RsVlanNs)


# --------------------------------------------------------------------------- Policies


def fabric_prot_pol(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Policies > Switch > Virtual Port Channel default."""
    Uni = cobra.model.pol.Uni(builder.root)
    Inst = cobra.model.fabric.Inst(Uni)
    for fabricProtPol in value:
        ProtPol = cobra.model.fabric.ProtPol(Inst, **fabricProtPol)
        builder.add(ProtPol)
        if "fabricExplicitGEp" in fabricProtPol:
            for fabricExplicitGEp in fabricProtPol["fabricExplicitGEp"]:
                ExplicitGEp = cobra.model.fabric.ExplicitGEp(ProtPol, **fabricExplicitGEp)
                builder.add(ExplicitGEp)
                if "fabricRsVpcInstPol" in fabricExplicitGEp:
                    RsVpcInstPol = cobra.model.fabric.RsVpcInstPol(
                        ExplicitGEp, **fabricExplicitGEp["fabricRsVpcInstPol"]
                    )
                    builder.add(RsVpcInstPol)
                if "fabricNodePEp" in fabricExplicitGEp:
                    for fabricNodePEp in fabricExplicitGEp["fabricNodePEp"]:
                        NodePEp = cobra.model.fabric.NodePEp(ExplicitGEp, **fabricNodePEp)
                        builder.add(NodePEp)


def fabric_h_if_pol(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Policies > Interface > Link Level."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    for fabricHIfPol in value:
        HIfPol = cobra.model.fabric.HIfPol(Infra, **fabricHIfPol)
        builder.add(HIfPol)


def qos_pfc_if_pol(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Policies > Interface > Priority Flow Control."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    for qosPfcIfPol in value:
        PfcIfPol = cobra.model.qos.PfcIfPol(Infra, **qosPfcIfPol)
        builder.add(PfcIfPol)


def cdp_if_pol(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Policies > Interface > CDP Interface."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    for cdpIfPol in value:
        IfPol = cobra.model.cdp.IfPol(Infra, **cdpIfPol)
        builder.add(IfPol)


def lldp_if_pol(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Policies > Interface > LLDP Interface."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    for lldpIfPol in value:
        IfPol = cobra.model.lldp.IfPol(Infra, **lldpIfPol)
        builder.add(IfPol)


def lacp_lag_pol(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Policies > Interface > Port Channel."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    for lacpLagPol in value:
        LagPol = cobra.model.lacp.LagPol(Infra, **lacpLagPol)
        builder.add(LagPol)


def stp_if_pol(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Policies > Interface > Spanning Tree Interface."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    for stpIfPol in value:
        IfPol = cobra.model.stp.IfPol(Infra, **stpIfPol)
        builder.add(IfPol)


def stormctrl_if_pol(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Policies > Interface > Storm Control."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    for stormctrlIfPol in value:
        IfPol = cobra.model.stormctrl.IfPol(Infra, **stormctrlIfPol)
        builder.add(IfPol)


def mcp_if_pol(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Policies > Interface > MCP Interface."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    for mcpIfPol in value:
        IfPol = cobra.model.mcp.IfPol(Infra, **mcpIfPol)
        builder.add(IfPol)


def bgp_inst_pol(builder: CobraBuilder, value: Any) -> None:
    """System Settings > All Tenants."""
    Inst = cobra.model.fabric.Inst(builder.uni)
    for bgpInstPol in value:
        InstPol = cobra.model.bgp.InstPol(Inst, **bgpInstPol)
        builder.add(InstPol)
        if "bgpAsP" in bgpInstPol:
            if not_nan_str(bgpInstPol["bgpAsP"], ["asn"]):
                AsP = cobra.model.bgp.AsP(InstPol, **bgpInstPol["bgpAsP"])
                builder.add(AsP)
        if "bgpRRP" in bgpInstPol:
            RRP = cobra.model.bgp.RRP(InstPol)
            builder.add(RRP)
            for bgpRRP in bgpInstPol["bgpRRP"]:
                if "bgpRRNodePEp" in bgpRRP:
                    RRNodePEp = cobra.model.bgp.RRNodePEp(RRP, **bgpRRP["bgpRRNodePEp"])
                    builder.add(RRNodePEp)
        if "ExtRRP" in bgpInstPol:
            ExtRRP = cobra.model.bgp.ExtRRP(InstPol)
            for extRRP in bgpInstPol["ExtRRP"]:
                RRNodePEp = cobra.model.bgp.RRNodePEp(ExtRRP, **extRRP)
                builder.add(RRNodePEp)


def coop_pol(builder: CobraBuilder, value: Any) -> None:
    """System Settings > COOP Group."""
    Inst = cobra.model.fabric.Inst(builder.uni)
    for coopPol in value:
        Pol = cobra.model.coop.Pol(Inst, **coopPol)
        builder.add(Pol)


def datetime_format(builder: CobraBuilder, value: Any) -> None:
    """System Settings > Date and Time."""
    Inst = cobra.model.fabric.Inst(builder.uni)
    for datetimeFormat in value:
        Format = cobra.model.datetime.Format(Inst, **datetimeFormat)
        builder.add(Format)


def aaa_fabric_sec(builder: CobraBuilder, value: Any) -> None:
    """System Settings > Fabric Security."""
    UserEp = cobra.model.aaa.UserEp(builder.uni)
    for aaaFabricSec in value:
        FabricSec = cobra.model.aaa.FabricSec(UserEp, **aaaFabricSec)
        builder.add(FabricSec)


def aaa_pre_login_banner(builder: CobraBuilder, value: Any) -> None:
    """System Settings > System Alias and Banners."""
    UserEp = cobra.model.aaa.UserEp(builder.uni)
    for aaaPreLoginBanner in value:
        PreLoginBanner = cobra.model.aaa.PreLoginBanner(UserEp, **aaaPreLoginBanner)
        builder.add(PreLoginBanner)


def pki_export_encryption_key(builder: CobraBuilder, value: Any) -> None:
    """System Settings > Fabric Security."""
    for pkiExportEncryptionKey in value:
        ExportEncryptionKey = cobra.model.pki.ExportEncryptionKey(
            builder.uni, **pkiExportEncryptionKey
        )
        builder.add(ExportEncryptionKey)


def ep_loop_protect_p(builder: CobraBuilder, value: Any) -> None:
    """System Settings > Enpoint Controls > The endpoint loop protection."""
    Infra = cobra.model.infra.Infra(builder.uni)
    for epLoopProtectP in value:
        LoopProtectP = cobra.model.ep.LoopProtectP(Infra, **epLoopProtectP)
        builder.add(LoopProtectP)


def ep_control_p(builder: CobraBuilder, value: Any) -> None:
    """System Settings > Enpoint Controls > Rogue EP Control."""
    Infra = cobra.model.infra.Infra(builder.uni)
    for epControlP in value:
        ControlP = cobra.model.ep.ControlP(Infra, **epControlP)
        builder.add(ControlP)


def ep_ip_aging_p(builder: CobraBuilder, value: Any) -> None:
    """System Settings > Enpoint Controls > IP Aging."""
    Infra = cobra.model.infra.Infra(builder.uni)
    for epIpAgingP in value:
        IpAgingP = cobra.model.ep.IpAgingP(Infra, **epIpAgingP)
        builder.add(IpAgingP)


def infra_set_pol(builder: CobraBuilder, value: Any) -> None:
    """System Settings > Fabric-Wide Settings."""
    Infra = cobra.model.infra.Infra(builder.uni)
    for infraSetPol in value:
        SetPol = cobra.model.infra.SetPol(Infra, **infraSetPol)
        builder.add(SetPol)


def isis_dom_pol(builder: CobraBuilder, value: Any) -> None:
    """System Settings > ISIS Policy."""
    Inst = cobra.model.fabric.Inst(builder.uni)
    for isisDomPol in value:
        DomPol = cobra.model.isis.DomPol(Inst, **isisDomPol)
        builder.add(DomPol)


def infra_port_track_pol(builder: CobraBuilder, value: Any) -> None:
    """System Settings > Port Tracking."""
    Infra = cobra.model.infra.Infra(builder.uni)
    for infraPortTrackPol in value:
        PortTrackPol = cobra.model.infra.PortTrackPol(Infra, **infraPortTrackPol)
        builder.add(PortTrackPol)


def mcp_inst_pol(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Access Policies > Global > MCP Instance Policy default."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    for mcpInstPol in value:
        InstPol = cobra.model.mcp.InstPol(Infra, **mcpInstPol)
        builder.add(InstPol)


def fabric_node_control(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Fabric Policies > Policies > Monitoring > Fabric Node Controls > default."""
    Uni = cobra.model.pol.Uni(builder.root)
    Inst = cobra.model.fabric.Inst(Uni)
    for fabricNodeControl in value:
        NodeControl = cobra.model.fabric.NodeControl(Inst, **fabricNodeControl)
        builder.add(NodeControl)


def geo_site(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Fabric Policies > Policies > Geolocation."""
    Uni = cobra.model.pol.Uni(builder.root)
    Inst = cobra.model.fabric.Inst(Uni)
    for geoSite in value:
        Site = cobra.model.geo.Site(Inst, **geoSite)
        builder.add(Site)
        if "geoBuilding" in geoSite:
            for geoBuilding in geoSite["geoBuilding"]:
                Building = cobra.model.geo.Building(Site, **geoBuilding)
                builder.add(Building)
                if "geoFloor" in geoBuilding:
                    for geoFloor in geoBuilding["geoFloor"]:
                        Floor = cobra.model.geo.Floor(Building, **geoFloor)
                        builder.add(Floor)
                        if "geoRoom" in geoFloor:
                            for geoRoom in geoFloor["geoRoom"]:
                                Room = cobra.model.geo.Room(Floor, **geoRoom)
                                builder.add(Room)
                                if "geoRow" in geoRoom:
                                    for geoRow in geoRoom["geoRow"]:
                                        Row = cobra.model.geo.Row(Room, **geoRow)
                                        builder.add(Row)
                                        if "geoRack" in geoRow:
                                            for geoRack in geoRow["geoRack"]:
                                                if not_nan_str(geoRack, ["name"]):
                                                    Rack = cobra.model.geo.Rack(Row, **geoRack)
                                                    builder.add(Rack)
                                                    if "geoRsNodeLocation" in geoRack:
                                                        for loc in geoRack["geoRsNodeLocation"]:
                                                            if not_nan_str(loc, ["tDn"]):
                                                                RsNodeLocation = (
                                                                    cobra.model.geo.RsNodeLocation(
                                                                        Rack, **loc
                                                                    )
                                                                )
                                                                builder.add(RsNodeLocation)


def latency_ptp_mode(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Fabric Policies > Policies > Monitoring > Fabric Node Controls > default."""
    Inst = cobra.model.fabric.Inst(builder.uni)
    for latencyPtpMode in value:
        PtpMode = cobra.model.latency.PtpMode(Inst, **latencyPtpMode)
        builder.add(PtpMode)


def infrazone_zone_p(builder: CobraBuilder, value: Any) -> None:
    """Fabric > Fabric Policies > Policies > Monitoring > Fabric Node Controls > default."""
    Uni = cobra.model.pol.Uni(builder.root)
    Infra = cobra.model.infra.Infra(Uni)
    ZoneP = cobra.model.infrazone.ZoneP(Infra, **value)
    builder.add(ZoneP)
    for infrazoneZone in value:
        if "Zone" in infrazoneZone:
            Zone = cobra.model.infrazone.Zone(ZoneP, **infrazoneZone["Zone"])
            builder.add(Zone)


# --------------------------------------------------------------------------- Registry

BUILDERS: dict[str, Handler] = {
    "fvTenant": fv_tenant,
    "fvAp": fv_ap,
    "fvAEPg": fv_aepg,
    "staticPath": static_path,
    "fvRsPathAtt": fv_rs_path_att,
    "tenant_application_uepg": tenant_application_uepg,
    "tenant_application_esg": tenant_application_esg,
    "fvBD": fv_bd,
    "fvCtx": fv_ctx,
    "tenant_network_l2out": tenant_network_l2out,
    "l3extOut": l3ext_out,
    "tenant_network_srmpls_l3out": tenant_network_srmpls_l3out,
    "tenant_dot1q_tunnel": tenant_dot1q_tunnel,
    "fvnsAddrInst": fvns_addr_inst,
    "mgmtGrp": mgmt_grp,
    "mgmtNodeGrp": mgmt_node_grp,
    "tenant_contract_standard": tenant_contract_standard,
    "tenant_contract_taboo": tenant_contract_taboo,
    "tenant_contract_imported": tenant_contract_imported,
    "tenant_contract_filter": tenant_contract_filter,
    "tenant_contract_oob": tenant_contract_oob,
    "tenant_policy_protocol_bfd": tenant_policy_protocol_bfd,
    "tenant_policy_protocol_bgp": tenant_policy_protocol_bgp,
    "tenant_policy_protocol_qos": tenant_policy_protocol_qos,
    "tenant_policy_protocol_dhcp": tenant_policy_protocol_dhcp,
    "tenant_policy_protocol_dataplane": tenant_policy_protocol_dataplane,
    "tenant_policy_protocol_eigrp": tenant_policy_protocol_eigrp,
    "tenant_policy_protocol_endpoint_retention": tenant_policy_protocol_endpoint_retention,
    "tenant_policy_protocol_firsthop_security": tenant_policy_protocol_firsthop_security,
    "tenant_policy_protocol_hsrp": tenant_policy_protocol_hsrp,
    "tenant_policy_protocol_igmp": tenant_policy_protocol_igmp,
    "tenant_policy_protocol_ip_sla": tenant_policy_protocol_ip_sla,
    "tenant_policy_protocol_pbr": tenant_policy_protocol_pbr,
    "tenant_policy_protocol_ospf": tenant_policy_protocol_ospf,
    "tenant_policy_protocol_pim": tenant_policy_protocol_pim,
    "tenant_policy_protocol_routemap_multicast": tenant_policy_protocol_routemap_multicast,
    "tenant_policy_protocol_routemap_control": tenant_policy_protocol_routemap_control,
    "tenant_policy_protocol_route_tag": tenant_policy_protocol_route_tag,
    "tenant_policy_troubleshooting_span": tenant_policy_troubleshooting_span,
    "tenant_policy_troubleshooting_traceroute": tenant_policy_troubleshooting_traceroute,
    "tenant_policy_monitoring": tenant_policy_monitoring,
    "tenant_policy_netflow": tenant_policy_netflow,
    "tenant_policy_vmm": tenant_policy_vmm,
    "tenant_service_parameter": tenant_service_parameter,
    "tenant_service_graph_template": tenant_service_graph_template,
    "tenant_service_router_configuration": tenant_service_router_configuration,
    "tenant_service_function_profile": tenant_service_function_profile,
    "tenant_service_devices": tenant_service_devices,
    "tenant_service_imported_device": tenant_service_imported_device,
    "tenant_service_device_policy": tenant_service_device_policy,
    "tenant_service_deployed_graph_instance": tenant_service_deployed_graph_instance,
    "tenant_service_deployed_device": tenant_service_deployed_device,
    "tenant_service_device_manager": tenant_service_device_manager,
    "tenant_service_chassis": tenant_service_chassis,
    "tenant_node_management_epg": tenant_node_management_epg,
    "tenant_external_management_profile": tenant_external_management_profile,
    "tenant_node_management_address": tenant_node_management_address,
    "tenant_node_management_static": tenant_node_management_static,
    "tenant_node_connection_group": tenant_node_connection_group,
    "fabricSetupPol": fabric_setup_pol,
    "fabricRsOosPath": fabric_rs_oos_path,
    "fabricSetupP": fabric_setup_p,
    "fabricNodeIdentPol": fabric_node_ident_pol,
    "fabricPodPGrp": fabric_pod_p_grp,
    "fabricPodP": fabric_pod_p,
    "fabric_switch_leaf_profile": fabric_switch_leaf_profile,
    "fabric_switch_leaf_policy_group": fabric_switch_leaf_policy_group,
    "fabric_switch_spine_profile": fabric_switch_spine_profile,
    "fabric_switch_spine_policy_group": fabric_switch_spine_policy_group,
    "fabric_module_leaf_profile": fabric_module_leaf_profile,
    "fabric_module_leaf_policy_group": fabric_module_leaf_policy_group,
    "fabric_module_spine_profile": fabric_module_spine_profile,
    "fabric_module_spine_policy_group": fabric_module_spine_policy_group,
    "fabric_interface_leaf_profile": fabric_interface_leaf_profile,
    "fabric_interface_leaf_policy_group": fabric_interface_leaf_policy_group,
    "fabric_interface_spine_profile": fabric_interface_spine_profile,
    "fabric_interface_spine_policy_group": fabric_interface_spine_policy_group,
    "datetimePol": datetime_pol,
    "snmpPol": snmp_pol,
    "commPol": comm_pol,
    "fabric_policy_switch_callhome": fabric_policy_switch_callhome,
    "infraNodeP": infra_node_p,
    "infraAccNodePGrp": infra_acc_node_p_grp,
    "infraSpineP": infra_spine_p,
    "infraSpineAccNodePGrp": infra_spine_acc_node_p_grp,
    "infraSpAccPortP": infra_sp_acc_port_p,
    "infraSpAccPortGrp": infra_sp_acc_port_grp,
    "infraAccPortP": infra_acc_port_p,
    "infraFexP": infra_fex_p,
    "infraAccPortGrp": infra_acc_port_grp,
    "infraAccBndlGrp": infra_acc_bndl_grp,
    "infraAttEntityP": infra_att_entity_p,
    "fvnsVlanInstP": fvns_vlan_inst_p,
    "physDomP": phys_dom_p,
    "l3extDomP": l3ext_dom_p,
    "l2extDomP": l2ext_dom_p,
    "fabricProtPol": fabric_prot_pol,
    "fabricHIfPol": fabric_h_if_pol,
    "qosPfcIfPol": qos_pfc_if_pol,
    "cdpIfPol": cdp_if_pol,
    "lldpIfPol": lldp_if_pol,
    "lacpLagPol": lacp_lag_pol,
    "stpIfPol": stp_if_pol,
    "stormctrlIfPol": stormctrl_if_pol,
    "mcpIfPol": mcp_if_pol,
    "bgpInstPol": bgp_inst_pol,
    "coopPol": coop_pol,
    "datetimeFormat": datetime_format,
    "aaaFabricSec": aaa_fabric_sec,
    "aaaPreLoginBanner": aaa_pre_login_banner,
    "pkiExportEncryptionKey": pki_export_encryption_key,
    "epLoopProtectP": ep_loop_protect_p,
    "epControlP": ep_control_p,
    "epIpAgingP": ep_ip_aging_p,
    "infraSetPol": infra_set_pol,
    "isisDomPol": isis_dom_pol,
    "infraPortTrackPol": infra_port_track_pol,
    "mcpInstPol": mcp_inst_pol,
    "fabricNodeControl": fabric_node_control,
    "geoSite": geo_site,
    "latencyPtpMode": latency_ptp_mode,
    "infrazoneZoneP": infrazone_zone_p,
}
