%global debug_package %nil
Name:                snappy-java
Version:             1.1.2.4
Release:             1
Summary:             Fast compressor/decompresser
License:             ASL 2.0
URL:                 http://xerial.org/snappy-java/
Source0:             https://github.com/xerial/snappy-java/archive/%{version}.tar.gz
Source1:             https://repo1.maven.org/maven2/org/xerial/snappy/%{name}/%{version}/%{name}-%{version}.pom
Patch0:              snappy-java-1.1.2-build.patch
Patch1:              snappy-java-1.1.2.4-lsnappy.patch

BuildRequires:       make gcc-c++ libstdc++-static snappy-devel
BuildRequires:       maven-local mvn(com.sun:tools) mvn(org.apache.felix:maven-bundle-plugin)
BuildRequires:       mvn(org.apache.felix:org.osgi.core)
BuildRequires:       mvn(org.apache.maven.plugins:maven-antrun-plugin)
Requires:            snappy

%description
A Java port of the snappy, a fast compresser/decompresser written in C++.

%package javadoc
Summary:             Javadoc for %{name}
BuildArch:           noarch

%description javadoc
This package contains the API documentation for %{name}.

%prep
%setup -q
find -name "*.class" -print -delete
find -name "*.jar" -print -delete
rm -r ./*sbt* project
find -name "*.jnilib" -print -delete
find -name "*.dll" -print -delete
find -name "*.so" -print -delete
find -name "*.a" -print -delete
find -name "*.h" -print -delete
%patch0 -p1
%patch1 -p1
cp %{SOURCE1} pom.xml
%pom_change_dep org.osgi: org.apache.felix::1.4.0
%pom_xpath_remove "pom:dependency[pom:scope = 'test']"
%pom_add_plugin org.apache.maven.plugins:maven-antrun-plugin . '
<dependencies>
 <dependency>
  <groupId>com.sun</groupId>
  <artifactId>tools</artifactId>
  <version>1.8.0</version>
 </dependency>
</dependencies>
<executions>
  <execution>
  <id>compile</id>
  <phase>process-classes</phase>
    <configuration>
      <target>
       <javac destdir="lib"
         srcdir="src/main/java"
         source="1.6" target="1.6" debug="on"
         classpathref="maven.plugin.classpath">
         <include name="**/OSInfo.java"/>
       </javac>
       <exec executable="make" failonerror="true">
        <arg line="%{?_smp_mflags}"/>
       </exec>
      </target>
    </configuration>
    <goals>
      <goal>run</goal>
    </goals>
  </execution>
</executions>'
%pom_add_plugin org.apache.felix:maven-bundle-plugin:2.5.4 . '
<extensions>true</extensions>
<configuration>
  <instructions>
    <Bundle-Activator>org.xerial.snappy.SnappyBundleActivator</Bundle-Activator>
    <Bundle-ActivationPolicy>lazy</Bundle-ActivationPolicy>
    <Bundle-SymbolicName>${project.groupId}.${project.artifactId}</Bundle-SymbolicName>
    <Bundle-Version>${project.version}</Bundle-Version>
    <Import-Package>org.osgi.framework,*</Import-Package>
  </instructions>
</configuration>
<executions>
  <execution>
    <id>bundle-manifest</id>
    <phase>process-classes</phase>
    <goals>
      <goal>manifest</goal>
    </goals>
  </execution>
</executions>'
%pom_add_plugin org.apache.maven.plugins:maven-compiler-plugin:3.0 . '
<configuration>
 <source>1.6</source>
 <target>1.6</target>
</configuration>'
chmod 644 NOTICE README.md
for file in LICENSE NOTICE README.md; do
 sed -i.orig 's|\r||g' $file
 touch -r $file.orig $file
 rm $file.orig
done

%build
CXXFLAGS="${CXXFLAGS:-%optflags}"
export CXXFLAGS
%mvn_build -f -- -Dproject.build.sourceEncoding=UTF-8

%install
%mvn_install

%files -f .mfiles
%doc README.md
%license LICENSE NOTICE

%files javadoc -f .mfiles-javadoc
%license LICENSE NOTICE

%changelog
* Tue Jul 28 2020 leiju <leiju4@huawei.com> - 1.1.2.4-1
- Package init
