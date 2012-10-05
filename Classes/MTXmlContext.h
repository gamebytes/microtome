//
// microtome - Copyright 2012 Three Rings Design

#import "MTContext.h"

@protocol MTPage;
@protocol MTXmlPropMarshaller;

@interface MTXmlContext : MTContext {
@protected
    NSMutableDictionary* _marshallers;
}

- (void)registerPropMarshaller:(id<MTXmlPropMarshaller>)marshaller;

- (id<MTPage>)loadPage:(GDataXMLElement*)xml name:(NSString*)name;
- (id<MTPage>)loadPage:(GDataXMLElement*)xml name:(NSString*)name requiredClass:(Class)requiredClass;

@end
